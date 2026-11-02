# Made by Claude (2026-10-21). Round 17: Settings > Account > Phone, the phone link as a QR code (collider_tunnel.py).
# Shown only on the computer that serves the app, and only once Cloudflare has given the link.
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def edit(rel, pairs):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        if s.count(old) != 1:
            sys.exit(f"{rel}: expected one match for: {old[:80]!r} (found {s.count(old)})")
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    print("edited", rel)


edit("lib/core/api/collider_api.dart", [
    ("""  String fileUrl(ColliderFile f) =>""",
     """  /// The phone link and its QR picture (data URL); empty away from the computer that serves the app.
  Future<(String, String)> phone() async {
    try {
      final r = await _dio.get('$_base/api/phone');
      return ('${r.data['link'] ?? ''}', '${r.data['qr'] ?? ''}');
    } catch (_) {
      return ('', '');
    }
  }

  String fileUrl(ColliderFile f) =>"""),
])

S = "lib/features/drawers/settings_drawer.dart"
edit(S, [
    ("""import 'package:flutter/material.dart';
import '../../../core/vision/vision_kit.dart';""", """import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../../core/api/collider_api.dart';
import '../../../core/vision/vision_kit.dart';"""),
    ("""class _SettingsDrawerState extends State<SettingsDrawer> {
  int _tab = 0;
""", """class _SettingsDrawerState extends State<SettingsDrawer> {
  int _tab = 0;
  String _phone = '', _qr = ''; // the phone link (Claude, 2026-10-21)

  @override
  void initState() {
    super.initState();
    ColliderApi.instance.phone().then((v) {
      if (mounted) setState(() => (_phone, _qr) = v);
    });
  }

  /// The phone link as a QR code for the phone's camera; a tap on it copies the link.
  void _showPhone() {
    final png = base64Decode(_qr.substring(_qr.indexOf(',') + 1));
    showDialog(
      context: context,
      barrierColor: VOverlay.scrim,
      builder: (ctx) => Center(
        child: VPress(
          onTap: () {
            Clipboard.setData(ClipboardData(text: _phone));
            Navigator.of(ctx).pop();
          },
          child: VGlass(
            material: VMaterial.modal,
            radius: 22,
            padding: const EdgeInsets.all(14),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: Image.memory(png, width: 220, height: 220, filterQuality: FilterQuality.none),
            ),
          ),
        ),
      ),
    );
  }
"""),
    ("""                                _link('Upgrade', w.onOpenUpgrade),""",
     """                                _link('Upgrade', w.onOpenUpgrade),
                                if (_phone.isNotEmpty && _qr.isNotEmpty) _link('Phone', _showPhone),"""),
])
