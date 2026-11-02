// The browser's bookmarks, history and settings. Made by Claude (2026-10-21).
// David, 21 Oct: "does our browser in collider have tabs, bookmarks, history, settings, all working? This should all be
// part of the package since they are stock features". Kept on the device (shared preferences), as Safari keeps them.
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

class BrowserPage {
  final String url;
  final String title;
  final DateTime time;
  const BrowserPage(this.url, this.title, this.time);
  Map<String, dynamic> toJson() => {'url': url, 'title': title, 't': time.millisecondsSinceEpoch};
  factory BrowserPage.fromJson(Map<String, dynamic> j) =>
      BrowserPage('${j['url']}', '${j['title'] ?? ''}', DateTime.fromMillisecondsSinceEpoch((j['t'] as num?)?.toInt() ?? 0));
}

class BrowserStore extends ChangeNotifier {
  BrowserStore._();
  static final BrowserStore instance = BrowserStore._();

  static const _kBookmarks = 'browser_bookmarks_v1';
  static const _kHistory = 'browser_history_v1';
  static const _kDesktop = 'browser_desktop_v1';
  static const historyKept = 1000;

  List<BrowserPage> bookmarks = [];
  List<BrowserPage> history = []; // newest first
  bool desktop = false; // ask sites for their computer pages
  bool _loaded = false;

  Future<void> init() async {
    if (_loaded) return;
    final p = await SharedPreferences.getInstance();
    List<BrowserPage> read(String k) {
      try {
        return [for (final j in (jsonDecode(p.getString(k) ?? '[]') as List)) BrowserPage.fromJson(Map<String, dynamic>.from(j as Map))];
      } catch (_) {
        return [];
      }
    }

    bookmarks = read(_kBookmarks);
    history = read(_kHistory);
    desktop = p.getBool(_kDesktop) ?? false;
    _loaded = true;
    notifyListeners();
  }

  Future<void> _save() async {
    final p = await SharedPreferences.getInstance();
    await p.setString(_kBookmarks, jsonEncode([for (final b in bookmarks) b.toJson()]));
    await p.setString(_kHistory, jsonEncode([for (final h in history) h.toJson()]));
    await p.setBool(_kDesktop, desktop);
  }

  bool isBookmarked(String url) => bookmarks.any((b) => b.url == url);

  void toggleBookmark(String url, String title) {
    if (isBookmarked(url)) {
      bookmarks.removeWhere((b) => b.url == url);
    } else {
      bookmarks.insert(0, BrowserPage(url, title, DateTime.now()));
    }
    notifyListeners();
    _save();
  }

  /// A page was shown. The same page again moves to the top rather than repeating.
  void visited(String url, String title) {
    if (url.isEmpty) return;
    history.removeWhere((h) => h.url == url);
    history.insert(0, BrowserPage(url, title, DateTime.now()));
    if (history.length > historyKept) history = history.sublist(0, historyKept);
    notifyListeners();
    _save();
  }

  void clearHistory() {
    history = [];
    notifyListeners();
    _save();
  }

  void setDesktop(bool v) {
    desktop = v;
    notifyListeners();
    _save();
  }
}
