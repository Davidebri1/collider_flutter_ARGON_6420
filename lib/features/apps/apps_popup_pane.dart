import 'package:flutter/services.dart';
import 'package:material_ui/material_ui.dart';
import '../../core/vision/vision_kit.dart';

/// Compact spatial app launcher popover hugging the 4x2 app icon group above the bottom dock.
/// Uses the standard VGlass modal container without stealing the full viewport behind a blocking scrim,
/// and animates symmetrically forward on entry and reverse on exit.
class AppsPopupPane extends StatefulWidget {
  final VoidCallback onClose;
  final VoidCallback onOpenSmartGen;
  final VoidCallback onOpenDiscoverMarket;
  final VoidCallback onOpenThemeGallery;
  final VoidCallback onOpenPremiumMarketplace;
  final VoidCallback onOpenFiles;
  final VoidCallback onOpenMusicPlayer;
  final VoidCallback onOpenBrowser;
  final VoidCallback onOpenDocuments;

  final String? themeArt;

  const AppsPopupPane({
    super.key,
    required this.onClose,
    required this.onOpenSmartGen,
    required this.onOpenDiscoverMarket,
    required this.onOpenThemeGallery,
    required this.onOpenPremiumMarketplace,
    required this.onOpenFiles,
    required this.onOpenMusicPlayer,
    required this.onOpenBrowser,
    required this.onOpenDocuments,
    this.themeArt,
  });

  @override
  State<AppsPopupPane> createState() => _AppsPopupPaneState();
}

class _AppsPopupPaneState extends State<AppsPopupPane> with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 220),
    reverseDuration: const Duration(milliseconds: 180),
  )..forward();
  late final Animation<double> _curve = CurvedAnimation(
    parent: _ctrl,
    curve: Curves.easeOutCubic,
  );
  bool _closing = false;

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  Future<void> _handleClose([VoidCallback? then]) async {
    if (_closing) return;
    _closing = true;
    try {
      await _ctrl.reverse();
    } catch (_) {}
    if (!mounted) return;
    widget.onClose();
    then?.call();
  }

  @override
  Widget build(BuildContext context) {
    final apps = [
      _App('Smart Gen', 'smart_gen', widget.onOpenSmartGen),
      _App('Discover Market', 'discover', widget.onOpenDiscoverMarket),
      _App('Documents', 'documents', widget.onOpenDocuments),
      _App('Files', 'files', widget.onOpenFiles),
      _App('Theme Gallery', 'theme_gallery', widget.onOpenThemeGallery),
      _App('Premium Theme Market', 'premium_market', widget.onOpenPremiumMarketplace),
      _App('Music Player', 'music', widget.onOpenMusicPlayer),
      _App('Browser', 'browser', widget.onOpenBrowser),
    ];

    final width = MediaQuery.of(context).size.width;
    const perRow = 4;
    final iconSize = width < 480 ? 48.0 : 58.0;
    final cell = iconSize + 20;

    final rows = <List<_App>>[];
    for (int i = 0; i < apps.length; i += perRow) {
      rows.add(apps.sublist(i, (i + perRow).clamp(0, apps.length)));
    }

    final grid = Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        for (int r = 0; r < rows.length; r++) ...[
          if (r > 0) const SizedBox(height: 10),
          Row(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              for (final a in rows[r])
                SizedBox(
                  width: cell,
                  child: _AppIcon(
                    app: a,
                    size: iconSize,
                    onTap: () => _handleClose(a.onTap),
                  ),
                ),
            ],
          ),
        ],
      ],
    );

    return CallbackShortcuts(
      bindings: <ShortcutActivator, VoidCallback>{
        const SingleActivator(LogicalKeyboardKey.escape): () => _handleClose(),
      },
      child: Focus(
        autofocus: true,
        child: Stack(
          fit: StackFit.expand,
          children: [
            // Transparent click-outside dismissal — leaves surrounding workspace unobstructed.
            GestureDetector(
              behavior: HitTestBehavior.opaque,
              onTap: () => _handleClose(),
              child: const SizedBox.expand(),
            ),
            Align(
              alignment: Alignment.bottomCenter,
              child: SafeArea(
                top: false,
                child: Padding(
                  padding: const EdgeInsets.only(bottom: 78, left: 12, right: 12),
                  child: AnimatedBuilder(
                    animation: _curve,
                    builder: (_, child) => Opacity(
                      opacity: _curve.value.clamp(0.0, 1.0),
                      child: Transform.translate(
                        offset: Offset(0, 14 * (1 - _curve.value)),
                        child: Transform.scale(
                          scale: 0.94 + 0.06 * _curve.value,
                          alignment: Alignment.bottomCenter,
                          child: child,
                        ),
                      ),
                    ),
                    child: GestureDetector(
                      onTap: () {},
                      child: Stack(
                        children: [
                          Padding(
                            padding: const EdgeInsets.only(top: 8, right: 8),
                            child: VGlass(
                              material: VMaterial.modal,
                              radius: VRadius.card,
                              padding: const EdgeInsets.fromLTRB(14, 14, 14, 10),
                              child: grid,
                            ),
                          ),
                          Positioned(
                            top: 0,
                            right: 0,
                            child: VCircleButton(
                              icon: Icons.close_rounded,
                              size: 26,
                              tooltip: 'Close',
                              floating: true,
                              onTap: () => _handleClose(),
                            ),
                          ),
                        ],
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

class _App {
  final String label;
  final String art;
  final VoidCallback onTap;
  const _App(this.label, this.art, this.onTap);
}

class _AppIcon extends StatefulWidget {
  final _App app;
  final double size;
  final VoidCallback onTap;
  const _AppIcon({required this.app, required this.size, required this.onTap});

  @override
  State<_AppIcon> createState() => _AppIconState();
}

class _AppIconState extends State<_AppIcon> {
  bool _hover = false;

  @override
  Widget build(BuildContext context) {
    final size = widget.size;
    return MouseRegion(
      onEnter: (_) => setState(() => _hover = true),
      onExit: (_) => setState(() => _hover = false),
      child: VPress(
        onTap: widget.onTap,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            AnimatedScale(
              scale: _hover ? 1.07 : 1.0,
              duration: VMotion.fast,
              curve: Curves.easeOutCubic,
              child: Container(
                width: size,
                height: size,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: _hover ? const Color(0x66FFFFFF) : const Color(0x28FFFFFF),
                    width: _hover ? 1.2 : 0.7,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: const Color(0x73000000),
                      blurRadius: _hover ? 18 : 12,
                      offset: Offset(0, _hover ? 8 : 5),
                    ),
                    if (_hover)
                      const BoxShadow(
                        color: Color(0x33FFFFFF),
                        blurRadius: 14,
                        spreadRadius: 1,
                      ),
                  ],
                ),
                child: ClipOval(
                  child: Image.asset(
                    'assets/icons/apps/claude_app_${widget.app.art}.png',
                    width: size,
                    height: size,
                    fit: BoxFit.cover,
                    filterQuality: FilterQuality.high,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 4),
            SizedBox(
              height: 24,
              child: Text(
                widget.app.label,
                maxLines: 2,
                textAlign: TextAlign.center,
                overflow: TextOverflow.ellipsis,
                style: VType.caption(
                  color: _hover ? Colors.white : VColors.textPrimary,
                  weight: _hover ? FontWeight.w600 : FontWeight.w500,
                ).copyWith(
                  fontSize: 9.5,
                  height: 11.5 / 9.5,
                  shadows: const [Shadow(color: Color(0xCC000000), blurRadius: 8)],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
