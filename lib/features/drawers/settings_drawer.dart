import 'dart:convert';

import 'package:material_ui/material_ui.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../core/api/collider_api.dart';
import '../../../core/platform/open_url.dart';
import '../../../core/vision/vision_kit.dart';

/// Persistent account & session housekeeping store (R01–R04, R59).
class AccountStore {
  static const _kSignedIn = 'collider_acct_signed_in_v1';
  static const _kName = 'collider_acct_name_v1';
  static const _kEmail = 'collider_acct_email_v1';
  static const _kProvider = 'collider_acct_provider_v1';
  static const _kTier = 'collider_acct_tier_v1';

  static bool signedIn = true;
  static String name = 'David Ebri';
  static String email = 'david@collider.ai';
  static String provider = 'Google';
  static String tier = 'Pro'; // Free | Pro | Elite
  static bool _loaded = false;

  static Future<void> load() async {
    if (_loaded) return;
    final p = await SharedPreferences.getInstance();
    signedIn = p.getBool(_kSignedIn) ?? true;
    name = p.getString(_kName) ?? 'David Ebri';
    email = p.getString(_kEmail) ?? 'david@collider.ai';
    provider = p.getString(_kProvider) ?? 'Google';
    tier = p.getString(_kTier) ?? 'Pro';
    _loaded = true;
  }

  static Future<void> signIn({
    required String newProvider,
    required String newName,
    required String newEmail,
    String? newTier,
  }) async {
    signedIn = true;
    provider = newProvider;
    name = newName;
    email = newEmail;
    if (newTier != null) tier = newTier;
    final p = await SharedPreferences.getInstance();
    await p.setBool(_kSignedIn, true);
    await p.setString(_kProvider, provider);
    await p.setString(_kName, name);
    await p.setString(_kEmail, email);
    await p.setString(_kTier, tier);
  }

  static Future<void> setTier(String newTier) async {
    tier = newTier;
    final p = await SharedPreferences.getInstance();
    await p.setString(_kTier, tier);
  }

  static Future<void> signOut() async {
    signedIn = false;
    provider = 'Guest';
    name = 'Guest Session';
    email = 'Local device storage only';
    tier = 'Free';
    final p = await SharedPreferences.getInstance();
    await p.setBool(_kSignedIn, false);
    await p.setString(_kProvider, provider);
    await p.setString(_kName, name);
    await p.setString(_kEmail, email);
    await p.setString(_kTier, tier);
  }
}

/// Settings & Account Drawer — Temporary / Demure Hologram Popup (R35, R47):
/// Floats directly over the live UI without hiding the Ticker or Composer.
class SettingsDrawer extends StatefulWidget {
  final VoidCallback onClose;
  final bool incognito;
  final bool autosave;
  final bool liveVideo;
  final ValueChanged<bool> onIncognito;
  final ValueChanged<bool> onAutosave;
  final ValueChanged<bool>? onLiveVideo;
  final VoidCallback onOpenPurchased;
  final VoidCallback onOpenUpgrade;

  const SettingsDrawer({
    super.key,
    required this.onClose,
    required this.incognito,
    required this.autosave,
    this.liveVideo = false,
    required this.onIncognito,
    required this.onAutosave,
    this.onLiveVideo,
    required this.onOpenPurchased,
    required this.onOpenUpgrade,
  });

  @override
  State<SettingsDrawer> createState() => _SettingsDrawerState();
}

class _SettingsDrawerState extends State<SettingsDrawer> with SingleTickerProviderStateMixin {
  int _tab = Uri.base.queryParameters['sub'] == 'account' ? 1 : 0;
  String _phone = '', _qr = '';
  bool _emailPrompt = false;
  final TextEditingController _emailCtrl = TextEditingController(text: 'david@collider.ai');
  late final AnimationController _ctrl = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 240),
    reverseDuration: const Duration(milliseconds: 190),
  )..forward();
  late final Animation<double> _curve = CurvedAnimation(
    parent: _ctrl,
    curve: Curves.easeOutCubic,
  );
  bool _closing = false;

  Future<void> _handleClose() async {
    if (_closing) return;
    _closing = true;
    try {
      await _ctrl.reverse();
    } catch (_) {}
    if (mounted) widget.onClose();
  }

  @override
  void initState() {
    super.initState();
    AccountStore.load().then((_) {
      if (mounted) setState(() {});
    });
    ColliderApi.instance.phone().then((v) {
      if (mounted) {
        setState(() {
          _phone = v.$1;
          _qr = v.$2;
        });
      }
    });
  }

  @override
  void dispose() {
    _ctrl.dispose();
    _emailCtrl.dispose();
    super.dispose();
  }

  void _showPhone() {
    final png = base64Decode(_qr.substring(_qr.indexOf(',') + 1));
    showDialog(
      context: context,
      barrierColor: Colors.transparent,
      builder: (ctx) => Center(
        child: VPress(
          onTap: () {
            Clipboard.setData(ClipboardData(text: _phone));
            Navigator.of(ctx).pop();
          },
          child: VGlass(
            material: VMaterial.modal,
            radius: VRadius.card,
            padding: const EdgeInsets.all(14),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(VRadius.row),
              child: Image.memory(png, width: 220, height: 220, filterQuality: FilterQuality.none),
            ),
          ),
        ),
      ),
    );
  }

  Widget _row(String label, Widget trailing, {String? sub}) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 6),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(label, maxLines: 1, overflow: TextOverflow.ellipsis, style: VType.callout(color: VColors.textPrimary, weight: FontWeight.w600).copyWith(fontSize: 12.0)),
                  if (sub != null) ...[
                    const SizedBox(height: 1),
                    Text(sub, maxLines: 1, overflow: TextOverflow.ellipsis, style: VType.caption(color: VColors.textSecondary).copyWith(fontSize: 10.0)),
                  ],
                ],
              ),
            ),
            const SizedBox(width: 12),
            trailing,
          ],
        ),
      );

  Widget _tabs() => Padding(
        padding: const EdgeInsets.only(bottom: 8),
        child: Row(children: [
          for (final (i, t) in const ['Settings', 'Account'].indexed) ...[
            if (i > 0) const SizedBox(width: 18),
            VPress(
              onTap: () => setState(() => _tab = i),
              child: Column(mainAxisSize: MainAxisSize.min, children: [
                Text(
                  t,
                  style: VType.callout(
                    color: i == _tab ? VColors.textPrimary : VColors.textSecondary,
                    weight: i == _tab ? FontWeight.w700 : FontWeight.w500,
                  ).copyWith(fontSize: 12.5),
                ),
                const SizedBox(height: 3),
                AnimatedContainer(
                  duration: VMotion.fast,
                  width: 20,
                  height: 2.0,
                  decoration: BoxDecoration(
                    color: i == _tab ? VColors.accentBlue : Colors.transparent,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ]),
            ),
          ],
          const Spacer(),
          VCircleButton(icon: Icons.close_rounded, size: 24, tooltip: 'Close', onTap: _handleClose),
        ]),
      );

  Widget _link(String label, VoidCallback onTap, {String? badge, Color? badgeColor}) => VPress(
        onTap: onTap,
        child: _row(
          label,
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (badge != null) ...[
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1),
                  decoration: BoxDecoration(
                    color: (badgeColor ?? VColors.accentBlue).withValues(alpha: 0.22),
                    borderRadius: BorderRadius.circular(VRadius.full),
                    border: Border.all(color: (badgeColor ?? VColors.accentBlue).withValues(alpha: 0.55), width: 0.6),
                  ),
                  child: Text(badge, style: VType.caption(color: Colors.white, weight: FontWeight.w600).copyWith(fontSize: 9.5)),
                ),
                const SizedBox(width: 4),
              ],
              const Icon(Icons.chevron_right_rounded, size: 14, color: VColors.textSecondary),
            ],
          ),
        ),
      );

  Widget _buildAccountTab(SettingsDrawer w) {
    final tierColor = switch (AccountStore.tier) {
      'Elite' => VColors.accentGold,
      'Pro' => VColors.accentBlue,
      _ => VColors.textSecondary,
    };
    final quotaText = switch (AccountStore.tier) {
      'Elite' => 'Unlimited Frontier + Cinema Video',
      'Pro' => '462 / 500 Pro Queries Left Today',
      _ => '12 / 20 Free Daily Queries Left',
    };

    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
          decoration: BoxDecoration(
            color: const Color(0x1FFFFFFF),
            borderRadius: BorderRadius.circular(VRadius.row),
            border: Border.all(color: tierColor.withValues(alpha: 0.45), width: 0.6),
          ),
          child: Row(
            children: [
              VAvatar(label: AccountStore.name, color: tierColor, size: 24),
              const SizedBox(width: 8),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(AccountStore.name, maxLines: 1, overflow: TextOverflow.ellipsis, style: VType.caption(color: Colors.white, weight: FontWeight.w600)),
                    Text(quotaText, maxLines: 1, overflow: TextOverflow.ellipsis, style: VType.metaCaption(color: VColors.textSecondary)),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: tierColor.withValues(alpha: 0.24),
                  borderRadius: BorderRadius.circular(VRadius.full),
                  border: Border.all(color: tierColor.withValues(alpha: 0.7), width: 0.6),
                ),
                child: Text(AccountStore.tier, style: VType.metaCaption(color: Colors.white, weight: FontWeight.w700)),
              ),
            ],
          ),
        ),
        const SizedBox(height: 6),
        Row(
          children: [
            for (final t in const ['Free', 'Pro', 'Elite']) ...[
              if (t != 'Free') const SizedBox(width: 4),
              Expanded(
                child: VPress(
                  onTap: () async {
                    await AccountStore.setTier(t);
                    if (mounted) setState(() {});
                  },
                  child: Container(
                    height: 22,
                    alignment: Alignment.center,
                    decoration: BoxDecoration(
                      color: AccountStore.tier == t ? VColors.fillActive : VColors.fillCell,
                      borderRadius: BorderRadius.circular(VRadius.full),
                      border: Border.all(color: AccountStore.tier == t ? VColors.borderHeavy : VColors.borderSubtle, width: 0.5),
                    ),
                    child: Text(t, style: VType.metaCaption(color: AccountStore.tier == t ? Colors.white : VColors.textSecondary, weight: FontWeight.w600)),
                  ),
                ),
              ),
            ],
          ],
        ),
        const SizedBox(height: 6),
        _link('Launch Configurator', () => openUrl('/config'), badge: 'Config'),
        _link('Purchased Themes & Media', w.onOpenPurchased),
        _link('Upgrade Plan & Quotas', w.onOpenUpgrade, badge: AccountStore.tier, badgeColor: tierColor),
        if (_phone.isNotEmpty && _qr.isNotEmpty) _link('Phone QR Instant Link', _showPhone, badge: 'Live'),
        if (AccountStore.signedIn)
          VPress(
            onTap: () async {
              await AccountStore.signOut();
              if (mounted) setState(() {});
            },
            child: _row(
              'Sign Out',
              const Icon(Icons.logout_rounded, size: 13, color: VColors.accentRed),
            ),
          ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final w = widget;
    return CallbackShortcuts(
      bindings: <ShortcutActivator, VoidCallback>{
        const SingleActivator(LogicalKeyboardKey.escape): _handleClose,
      },
      child: Focus(
        autofocus: true,
        child: Stack(
          fit: StackFit.expand,
          children: [
            GestureDetector(
              behavior: HitTestBehavior.opaque,
              onTap: _handleClose,
              child: const SizedBox.expand(),
            ),
            Align(
              alignment: Alignment.bottomCenter,
              child: SafeArea(
                top: false,
                child: Padding(
                  padding: const EdgeInsets.only(bottom: 78, left: 20, right: 20),
                  child: AnimatedBuilder(
                    animation: _curve,
                    builder: (_, child) => Opacity(
                      opacity: _curve.value.clamp(0.0, 1.0),
                      child: Transform.translate(
                        offset: Offset(0, 14 * (1 - _curve.value)),
                        child: Transform.scale(
                          scale: 0.96 + 0.04 * _curve.value,
                          alignment: Alignment.bottomCenter,
                          child: child,
                        ),
                      ),
                    ),
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(minWidth: 250, maxWidth: 292, maxHeight: 310),
                      child: GestureDetector(
                        onTap: () {},
                        child: VGlass(
                          material: VMaterial.modal,
                          radius: VRadius.card,
                          padding: const EdgeInsets.fromLTRB(16, 14, 16, 12),
                          child: AnimatedSize(
                            duration: VMotion.fast,
                            curve: Curves.easeOutCubic,
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              crossAxisAlignment: CrossAxisAlignment.stretch,
                              children: [
                                _tabs(),
                                Flexible(
                                  child: EdgeFade(
                                    fadeHeight: 14,
                                    child: SingleChildScrollView(
                                      physics: const BouncingScrollPhysics(),
                                      child: _tab == 0
                                          ? Column(
                                              mainAxisSize: MainAxisSize.min,
                                              crossAxisAlignment: CrossAxisAlignment.stretch,
                                              children: [
                                                _row(
                                                  'Incognito Session',
                                                  VToggle(value: w.incognito, onChanged: w.onIncognito),
                                                  sub: 'Zero history or disk trace',
                                                ),
                                                _row(
                                                  'Save to History',
                                                  VToggle(value: w.autosave, onChanged: w.incognito ? null : w.onAutosave),
                                                  sub: 'Persist threads & Smart Gen',
                                                ),
                                                if (w.onLiveVideo != null)
                                                  _row(
                                                    'Live Video Wallpaper',
                                                    VToggle(value: w.liveVideo, onChanged: w.onLiveVideo),
                                                    sub: 'Off saves GPU on resting Home',
                                                  ),
                                                _link('Launch Configurator', () => openUrl('/config'), badge: '6420'),
                                                _link('Purchased Themes', w.onOpenPurchased),
                                                _link('Upgrade Plan', w.onOpenUpgrade),
                                              ],
                                            )
                                          : _buildAccountTab(w),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
