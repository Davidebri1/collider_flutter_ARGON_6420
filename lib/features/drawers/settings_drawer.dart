import 'dart:convert';

import 'package:material_ui/material_ui.dart';
import 'package:flutter/services.dart';
import '../../../core/api/collider_api.dart';
import '../../../core/vision/vision_kit.dart';

/// Settings & Account Drawer.
class SettingsDrawer extends StatefulWidget {
  final VoidCallback onClose;
  final bool incognito;
  final bool autosave;
  final ValueChanged<bool> onIncognito;
  final ValueChanged<bool> onAutosave;
  final VoidCallback onOpenPurchased;
  final VoidCallback onOpenUpgrade;

  const SettingsDrawer({
    super.key,
    required this.onClose,
    required this.incognito,
    required this.autosave,
    required this.onIncognito,
    required this.onAutosave,
    required this.onOpenPurchased,
    required this.onOpenUpgrade,
  });

  @override
  State<SettingsDrawer> createState() => _SettingsDrawerState();
}

class _SettingsDrawerState extends State<SettingsDrawer> {
  int _tab = 0;
  String _phone = '', _qr = '';

  @override
  void initState() {
    super.initState();
    ColliderApi.instance.phone().then((v) {
      if (mounted) {
        setState(() {
          _phone = v.$1;
          _qr = v.$2;
        });
      }
    });
  }

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

  Widget _row(String label, Widget trailing) => SizedBox(
        height: 36,
        child: Row(
          children: [
            Text(label, maxLines: 1, style: VType.callout(color: const Color(0xF5FFFFFF), weight: FontWeight.w500).copyWith(fontSize: 11)),
            const SizedBox(width: 20),
            const Spacer(),
            trailing,
          ],
        ),
      );

  Widget _tabs() => Padding(
        padding: const EdgeInsets.only(bottom: 6),
        child: Row(children: [
          for (final (i, t) in const ['Settings', 'Account'].indexed) ...[
            if (i > 0) const SizedBox(width: 16),
            VPress(
              onTap: () => setState(() => _tab = i),
              child: Column(mainAxisSize: MainAxisSize.min, children: [
                Text(
                  t,
                  style: VType.caption(
                    color: i == _tab ? VColors.textPrimary : VColors.textSecondary,
                    weight: i == _tab ? FontWeight.w600 : FontWeight.w500,
                  ).copyWith(fontSize: 11),
                ),
                const SizedBox(height: 3),
                AnimatedContainer(
                  duration: VMotion.fast,
                  width: 16,
                  height: 2,
                  decoration: BoxDecoration(
                    color: i == _tab ? VColors.accentBlue : Colors.transparent,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ]),
            ),
          ],
        ]),
      );

  Widget _link(String label, VoidCallback onTap) => VPress(
        onTap: onTap,
        child: _row(label, const Icon(CupertinoIcons.chevron_forward, size: 14, color: VColors.textSecondary)),
      );

  @override
  Widget build(BuildContext context) {
    final w = widget;
    return Stack(
      fit: StackFit.expand,
      children: [
        VScrim(onTap: w.onClose, soft: true),
        Align(
          alignment: Alignment.bottomCenter,
          child: SafeArea(
            top: false,
            child: Padding(
              padding: const EdgeInsets.only(bottom: 86),
              child: ConstrainedBox(
                constraints: const BoxConstraints(minWidth: 205, maxWidth: 240),
                child: GestureDetector(
                  onTap: () {},
                  child: VGlass(
                    material: VMaterial.modal,
                    radius: 22,
                    padding: const EdgeInsets.fromLTRB(20, 12, 16, 10),
                    child: AnimatedSize(
                      duration: VMotion.fast,
                      curve: Curves.easeOutCubic,
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          _tabs(),
                          if (_tab == 0)
                            Column(
                              mainAxisSize: MainAxisSize.min,
                              crossAxisAlignment: CrossAxisAlignment.stretch,
                              children: [
                                _row('Incognito', VToggle(value: w.incognito, onChanged: w.onIncognito)),
                                _row('Save to History', VToggle(value: w.autosave, onChanged: w.incognito ? null : w.onAutosave)),
                              ],
                            )
                          else
                            Column(
                              mainAxisSize: MainAxisSize.min,
                              crossAxisAlignment: CrossAxisAlignment.stretch,
                              children: [
                                _link('Purchased', w.onOpenPurchased),
                                _link('Upgrade', w.onOpenUpgrade),
                                if (_phone.isNotEmpty && _qr.isNotEmpty) _link('Phone', _showPhone),
                              ],
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
      ],
    );
  }
}
