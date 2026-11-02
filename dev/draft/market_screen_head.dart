import 'dart:async';

import 'package:material_ui/material_ui.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../../core/api/collider_api.dart';
import '../../../core/media/theme_cloud.dart';
import '../../../core/media/video_window.dart';
import '../../../core/platform/open_url.dart';
import '../../../core/vision/vision_kit.dart';
import '../../../core/vision/work_surface.dart';
import '../../../models/theme_def.dart';
import '../../theme/theme_living_media.dart';
import '../../theme/theme_pack_store.dart';

/// Discover Market. Rebuilt by Claude (2026-10-18) on the layout of Grok's Imagine feed (Mobbin, Grok iOS):
///  - the feed: two or more columns of tall tiles edge to edge, a video tile marked with a small play button;
///  - a tile opens Collider's own video player (VideoWindow, Figma row 19); its "more" holds save, download and share;
///    a sideways swipe moves to the next one;
///  - the side rail: Discover, and My Gallery for the saved ones.
/// What it shows: David's live wallpapers from his Cloudflare bucket (ThemeCloud), and (Claude, 2026-10-20) what is
/// made here through fal: the bar at the foot of the pane makes pictures or a video from words, as Imagine does.
/// It is a pane, like Smart Gen. The labels are David's: "I'm discover market. so dont copy words."
class MarketScreen extends StatefulWidget {
  final VoidCallback onClose;
  final String view; // 'discover' or 'gallery'

  const MarketScreen({super.key, required this.onClose, this.view = 'discover'});

  @override
  State<MarketScreen> createState() => _MarketScreenState();
}

class _MarketScreenState extends State<MarketScreen> {
  static const _savedKey = 'market_saved_v1';
  static final Set<String> _savedCache = {};
  static bool _savedLoaded = false;
  final Set<String> _saved = {..._savedCache};
  int? _open; // index into the list on show
  List<Creation> _made = const [];
  Timer? _poll;
  (Creation, Map<String, dynamic>)? _picture; // a picture opened large
  Map<String, dynamic>? _film; // a made video opened

  @override
  void initState() {
    super.initState();
    ThemeCloud.instance.addListener(_changed);
    ThemeCloud.instance.init();
    ThemePackStore.instance.init();
    _refresh();
    if (!_savedLoaded) {
      SharedPreferences.getInstance().then((p) {
        final list = p.getStringList(_savedKey) ?? const [];
        _savedCache
          ..clear()
          ..addAll(list);
        _savedLoaded = true;
        if (!mounted) return;
        setState(() => _saved
          ..clear()
          ..addAll(_savedCache));
      });
    }
  }

  @override
  void dispose() {
    _poll?.cancel();
    ThemeCloud.instance.removeListener(_changed);
    super.dispose();
  }

  void _changed() => mounted ? setState(() {}) : null;

  /// What has been made; while anything is still being made, asked again every two seconds.
  Future<void> _refresh() async {
    final list = await ColliderApi.instance.creations();
    if (!mounted) return;
    setState(() => _made = list);
    _poll?.cancel();
    if (list.any((c) => c.making)) _poll = Timer(const Duration(seconds: 2), _refresh);
  }

  Future<void> _make(String text, bool video) async {
    await ColliderApi.instance.make(text, video ? 'video' : 'image');
    await _refresh();
  }

  Future<void> _motion(Creation c) async {
    setState(() => _picture = null);
    await ColliderApi.instance.make(c.text, 'motion', from: c.id);
    await _refresh();
  }

  List<WallpaperTheme> get _items {
    final all = [for (final t in ThemeCloud.instance.themes) if (t.videoPath != null) t];
    return widget.view == 'gallery' ? [for (final t in all) if (_saved.contains(t.id)) t] : all;
  }

  /// One tile per picture or video made; while making, the tiles it will fill.
  List<(Creation, Map<String, dynamic>?)> get _madeTiles {
    final out = <(Creation, Map<String, dynamic>?)>[];
    for (final c in _made) {
      if (widget.view == 'gallery' && !c.media.any((m) => _saved.contains('c:${m['name']}'))) continue;
      if (c.media.isEmpty) {
        for (var i = 0; i < (c.kind == 'image' && c.making ? 4 : 1); i++) {
          out.add((c, null));
        }
      } else {
        for (final m in c.media) {
          if (widget.view != 'gallery' || _saved.contains('c:${m['name']}')) out.add((c, m));
        }
      }
    }
    return out;
  }

  Future<void> _toggleSaveId(String id) async {
    setState(() {
      if (_saved.contains(id)) {
        _saved.remove(id);
        _savedCache.remove(id);
      } else {
        _saved.add(id);
        _savedCache.add(id);
      }
    });
    (await SharedPreferences.getInstance()).setStringList(_savedKey, _saved.toList()..sort());
  }

  Future<void> _toggleSave(WallpaperTheme t) => _toggleSaveId(t.id);

  @override
  void didUpdateWidget(MarketScreen old) {
    super.didUpdateWidget(old);
    if (old.view != widget.view) _open = null;
  }

  void _tapMade(Creation c, Map<String, dynamic>? m) {
    if (c.status == 'failed') {
      ColliderApi.instance.make(c.text, c.kind, from: c.from).then((_) => _refresh());
      return;
    }
    if (m == null) return;
    setState(() => m['kind'] == 'video' ? _film = m : _picture = (c, m));
  }

  @override
  Widget build(BuildContext context) {
    final items = _items;
    final made = _madeTiles;
    return Stack(
      children: [
        VWorkSurface(
          title: 'Discover Market',
          onClose: widget.onClose,
          child: Stack(children: [
            Positioned.fill(child: _grid(made, items)),
            Positioned(left: VSpace.md, right: VSpace.md, bottom: VSpace.md, child: _MakeBar(onMake: _make)),
          ]),
        ),
        if (_open != null && _open! < items.length)
          Positioned.fill(
            child: _Viewer(
              items: items,
              start: _open!,
              saved: _saved,
              onSave: _toggleSave,
              onClose: () => setState(() => _open = null),
            ),
          ),
        if (_picture != null)
          Positioned.fill(
            child: _PictureWindow(
              c: _picture!.$1,
              m: _picture!.$2,
              saved: _saved.contains('c:${_picture!.$2['name']}'),
              onClose: () => setState(() => _picture = null),
              onMotion: () => _motion(_picture!.$1),
              onSave: () => _toggleSaveId('c:${_picture!.$2['name']}'),
            ),
          ),
        if (_film != null)
          Positioned.fill(
            child: Stack(children: [
              GestureDetector(
                behavior: HitTestBehavior.opaque,
                onTap: () => setState(() => _film = null),
                child: const ColoredBox(color: Color(0xCC06080E), child: SizedBox.expand()),
              ),
              Padding(
                padding: const EdgeInsets.fromLTRB(VSpace.md, VSpace.lg, VSpace.md, VSpace.md),
                child: VideoWindow(
                  key: ValueKey(_film!['name']),
                  url: ColliderApi.instance.fileUrl(ColliderFile('${_film!['name']}', 'generated', 0, DateTime.now(), 'video', '${_film!['url']}')),
                  onClose: () => setState(() => _film = null),
                ),
              ),
            ]),
          ),
      ],
    );
  }

  Widget _grid(List<(Creation, Map<String, dynamic>?)> made, List<WallpaperTheme> items) {
    if (items.isEmpty && made.isEmpty) return const SizedBox.shrink();
    return LayoutBuilder(builder: (context, c) {
      final cols = (c.maxWidth / 200).floor().clamp(2, 5);
      return ClipRRect(
        borderRadius: const BorderRadius.vertical(bottom: Radius.circular(VRadius.xl)),
        child: EdgeFade(
          focus: FadeFocus.top,
          child: GridView.builder(
            // room at the foot for the bar, so the last row can be scrolled clear of it
            padding: const EdgeInsets.fromLTRB(2, 0, 2, 96),
            physics: const BouncingScrollPhysics(),
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(crossAxisCount: cols, mainAxisSpacing: 2, crossAxisSpacing: 2, childAspectRatio: 0.78),
            itemCount: made.length + items.length,
            itemBuilder: (_, i) {
              if (i < made.length) {
                final (cr, m) = made[i];
                return VPress(onTap: () => _tapMade(cr, m), child: _CreationTile(cr, m));
              }
              final k = i - made.length;
              return VPress(onTap: () => setState(() => _open = k), child: _Tile(theme: items[k]));
            },
          ),
        ),
      );
    });
  }
}
