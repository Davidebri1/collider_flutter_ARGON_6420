// Theme packs for sale. Rewritten by Claude (2026-10-17) for David: the front end of in-app purchase.
//  - Every live wallpaper is a pack, sold as a non-consumable product "collider.theme.<number>" (tools/collider_server.py).
//  - On iOS, macOS and Android the purchase goes through the App Store or Google Play (package in_app_purchase).
//    The store shows its own payment sheet and its own confirmation; the app adds only what the store leaves out.
//  - Bypass (the launch window's Purchases switch, saved in data\collider_config.json): a Buy completes at once,
//    for development. The app then shows the confirmation the store would have shown.
//  - The price on a pack is the store's own local price once the store has answered; until then the catalog's.
import '../../core/api/collider_api.dart';
import 'dart:async';

import 'package:dio/dio.dart';
import 'package:cupertino_ui/cupertino_ui.dart';
import 'package:flutter/foundation.dart';
import 'package:material_ui/material_ui.dart';
import 'package:in_app_purchase/in_app_purchase.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../models/theme_def.dart';

enum PurchaseOutcome { purchased, pending, cancelled, failed, storeUnavailable, itemUnavailable }

class ThemePackStore extends ChangeNotifier {
  ThemePackStore._();
  static final ThemePackStore instance = ThemePackStore._();

  static const _prefsKey = 'theme_pack_unlocked_ids';

  final Set<String> _unlocked = {};
  bool _ready = false;
  bool get isReady => _ready;
  Future<void>? _starting;

  bool _bypass = false;

  /// Purchases complete without a store (development).
  bool get bypass => _bypass;

  final Map<String, ProductDetails> _products = {};
  final Map<String, String> _packOf = {}; // product id -> pack id
  final Map<String, Completer<PurchaseOutcome>> _waiting = {};
  StreamSubscription<List<PurchaseDetails>>? _sub;

  static bool get _hasStore =>
      !kIsWeb &&
      (defaultTargetPlatform == TargetPlatform.iOS ||
          defaultTargetPlatform == TargetPlatform.android ||
          defaultTargetPlatform == TargetPlatform.macOS);

  Future<void> init() => _starting ??= _start();

  Future<void> _start() async {
    final prefs = await SharedPreferences.getInstance();
    _unlocked
      ..clear()
      ..addAll(prefs.getStringList(_prefsKey) ?? const <String>[]);
    if (kIsWeb) {
      try {
        final r = await Dio().get<Map<String, dynamic>>('${ColliderApi.base}/api/store');
        _bypass = r.data?['bypass'] == true;
      } catch (_) {}
    }
    if (_hasStore) {
      _sub = InAppPurchase.instance.purchaseStream.listen(_onPurchases, onError: (_) {});
    }
    _ready = true;
    notifyListeners();
  }

  bool isUnlocked(String id) => _unlocked.contains(id);

  /// Purchased pack ids (Files > Purchased and the Theme Gallery list them).
  Set<String> get unlocked => Set.unmodifiable(_unlocked);

  String productIdFor(WallpaperTheme t) => t.productId ?? 'collider.theme.${t.id}';

  /// The store's local price when it has answered, otherwise the catalog's.
  String? priceFor(WallpaperTheme t) => _products[productIdFor(t)]?.price ?? t.priceLabel;

  /// Asks the store for the local prices of these packs.
  Future<void> loadPrices(Iterable<WallpaperTheme> packs) async {
    await init();
    if (!_hasStore) return;
    final ids = {for (final t in packs) productIdFor(t)}..removeAll(_products.keys);
    if (ids.isEmpty) return;
    try {
      if (!await InAppPurchase.instance.isAvailable()) return;
      final r = await InAppPurchase.instance.queryProductDetails(ids);
      for (final p in r.productDetails) {
        _products[p.id] = p;
      }
      notifyListeners();
    } catch (_) {}
  }

  Future<PurchaseOutcome> buy(WallpaperTheme t) async {
    await init();
    if (isUnlocked(t.id)) return PurchaseOutcome.purchased;
    if (_bypass) {
      await _unlock(t.id);
      return PurchaseOutcome.purchased;
    }
    if (!_hasStore) return PurchaseOutcome.storeUnavailable;
    final iap = InAppPurchase.instance;
    final pid = productIdFor(t);
    _packOf[pid] = t.id;
    try {
      if (!await iap.isAvailable()) return PurchaseOutcome.storeUnavailable;
      var product = _products[pid];
      if (product == null) {
        final r = await iap.queryProductDetails({pid});
        if (r.productDetails.isEmpty) return PurchaseOutcome.itemUnavailable;
        product = _products[pid] = r.productDetails.first;
      }
      final done = Completer<PurchaseOutcome>();
      _waiting[pid] = done;
      if (!await iap.buyNonConsumable(purchaseParam: PurchaseParam(productDetails: product))) {
        _waiting.remove(pid);
        return PurchaseOutcome.failed;
      }
      return done.future;
    } catch (_) {
      _waiting.remove(pid);
      return PurchaseOutcome.failed;
    }
  }

  /// Brings back packs bought on another device (the stores require the option).
  Future<void> restorePurchases() async {
    await init();
    if (_hasStore) {
      try {
        await InAppPurchase.instance.restorePurchases();
      } catch (_) {}
    }
  }

  Future<void> _onPurchases(List<PurchaseDetails> list) async {
    for (final p in list) {
      final outcome = switch (p.status) {
        PurchaseStatus.purchased || PurchaseStatus.restored => PurchaseOutcome.purchased,
        PurchaseStatus.pending => PurchaseOutcome.pending,
        PurchaseStatus.canceled => PurchaseOutcome.cancelled,
        PurchaseStatus.error => PurchaseOutcome.failed,
      };
      if (outcome == PurchaseOutcome.purchased) {
        await _unlock(_packOf[p.productID] ?? p.productID.replaceFirst('collider.theme.', ''));
      }
      if (p.pendingCompletePurchase) {
        try {
          await InAppPurchase.instance.completePurchase(p);
        } catch (_) {}
      }
      final waiting = _waiting[p.productID];
      if (waiting != null && !waiting.isCompleted) {
        waiting.complete(outcome);
        if (outcome != PurchaseOutcome.pending) _waiting.remove(p.productID);
      }
    }
  }

  Future<void> _unlock(String id) async {
    _unlocked.add(id);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList(_prefsKey, _unlocked.toList()..sort());
    notifyListeners();
  }

  @override
  void dispose() {
    _sub?.cancel();
    super.dispose();
  }
}

/// What the app says after a purchase, in the platform's own words and look: an alert on Apple devices, a snackbar on
/// Android. Where the store already said it (its payment sheet confirms a purchase; a cancel needs nothing), the app
/// stays quiet.
class PurchaseNotice {
  static bool get _android => defaultTargetPlatform == TargetPlatform.android;
  static bool get _apple =>
      defaultTargetPlatform == TargetPlatform.iOS || defaultTargetPlatform == TargetPlatform.macOS;

  static Future<void> show(BuildContext context, PurchaseOutcome o, {required bool bypassed}) async {
    final (String? title, String? body, String? snack) = switch (o) {
      PurchaseOutcome.purchased when bypassed => ("You're all set.", 'Your purchase was successful.', 'Payment successful'),
      PurchaseOutcome.purchased || PurchaseOutcome.cancelled => (null, null, null),
      PurchaseOutcome.pending => (
          'Purchase Pending',
          "Your purchase is waiting for approval. You'll get it as soon as it's approved.",
          "Purchase pending. You'll get it once payment is complete.",
        ),
      PurchaseOutcome.failed => ('Purchase Failed', 'Your purchase could not be completed. Try again later.', 'Purchase failed. Try again.'),
      PurchaseOutcome.itemUnavailable => ('Item Unavailable', "This item isn't available right now.", "This item isn't available right now."),
      PurchaseOutcome.storeUnavailable => (
          _apple ? 'Cannot Connect to App Store' : 'Purchases Unavailable',
          _apple ? null : "In-app purchases aren't available on this device.",
          "Can't connect to Google Play. Try again.",
        ),
    };
    if (title == null || !context.mounted) return;
    if (_android) {
      ScaffoldMessenger.maybeOf(context)
        ?..hideCurrentSnackBar()
        ..showSnackBar(SnackBar(content: Text(snack!), behavior: SnackBarBehavior.floating, duration: const Duration(seconds: 4)));
      return;
    }
    await showCupertinoDialog<void>(
      context: context,
      barrierDismissible: true,
      builder: (c) => CupertinoTheme(
        data: const CupertinoThemeData(brightness: Brightness.dark),
        child: CupertinoAlertDialog(
          title: Text(title),
          content: body == null ? null : Text(body),
          actions: [CupertinoDialogAction(isDefaultAction: true, onPressed: () => Navigator.of(c).pop(), child: const Text('OK'))],
        ),
      ),
    );
  }
}
