import 'dart:async';

import 'package:material_ui/material_ui.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../../core/api/collider_api.dart';
import '../../../core/drafts.dart';
import '../../../core/media/theme_cloud.dart';
import '../../../core/vision/vision_kit.dart';
import '../../../models/theme_def.dart';
import '../../media/generations_pane.dart' show BreathingTile;
import '../../media/picture_viewer.dart';

/// Discover Market — Grok Imagine + Unsplash masonry showcase with lazy viewport building and title captions.
class MarketScreen extends StatefulWidget {
  final VoidCallback onClose;
  final String view; // 'discover' or 'gallery'
  final ValueChanged<String> onImagine;
  final ValueChanged<String> onRemix;

  const MarketScreen({
    super.key,
    required this.onClose,
    required this.onImagine,
    required this.onRemix,
    this.view = 'discover',
  });

  @override
  State<MarketScreen> createState() => _MarketScreenState();
}

class _Item {
  final String id;
  final String title;
  final String url;
  final double aspect;
  final String? fileRef;
  final WallpaperTheme? theme;
  const _Item({
    required this.id,
    required this.title,
    required this.url,
    required this.aspect,
    this.fileRef,
    this.theme,
  });
}

class _MarketScreenState extends State<MarketScreen> {
  static const _savedKey = 'market_saved_v1';
  static final Set<String> _savedCache = {};
  static bool _savedLoaded = false;
  final Set<String> _saved = {..._savedCache};
  List<Creation> _made = const [];
  Timer? _poll;
  final _text = Drafts.text('discover');

  @override
  void initState() {
    super.initState();
    ThemeCloud.instance.addListener(_changed);
    ThemeCloud.instance.init();
    _refresh();
    if (!_savedLoaded) {
      SharedPreferences.getInstance().then((p) {
        _savedCache
          ..clear()
          ..addAll(p.getStringList(_savedKey) ?? const []);
        _savedLoaded = true;
        if (mounted) {
          setState(() => _saved
            ..clear()
            ..addAll(_savedCache));
        }
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

  Future<void> _refresh() async {
    final list = await ColliderApi.instance.creations();
    if (!mounted) return;
    setState(() => _made = list);
    _poll?.cancel();
    if (list.any((c) => c.making)) _poll = Timer(const Duration(seconds: 3), _refresh);
  }

  List<_Item> get _items {
    final api = ColliderApi.instance;
    final seenTitles = <String>{};
    final out = <_Item>[
      for (final c in _made)
        if (c.kind == 'image' && c.status == 'done')
          for (final m in c.media)
            if (m['kind'] != 'video')
              _Item(
                id: 'c:${m['name']}',
                title: c.text.isNotEmpty ? c.text : '${m['name']}',
                url: api.fileUrl(ColliderFile('${m['name']}', 'generated', 0, DateTime.now(), 'image', '${m['url']}')),
                aspect: (m['width'] is num && m['height'] is num && (m['height'] as num) > 0)
                    ? (m['width'] as num) / (m['height'] as num)
                    : 9 / 16,
                fileRef: 'generated/${m['name']}',
              ),
      for (final t in ThemeCloud.instance.themes)
        if (seenTitles.add(t.name.toLowerCase().trim()))
          _Item(id: t.id, title: t.name, url: t.assetPath, aspect: 1168 / 1728, theme: t),
    ];
    return widget.view == 'gallery' ? [for (final i in out) if (_saved.contains(i.id)) i] : out;
  }

  Future<void> _save(ViewedPicture p) async {
    setState(() {
      if (_saved.contains(p.id)) {
        _saved.remove(p.id);
        _savedCache.remove(p.id);
      } else {
        _saved.add(p.id);
        _savedCache.add(p.id);
      }
    });
    (await SharedPreferences.getInstance()).setStringList(_savedKey, _saved.toList()..sort());
  }

  Future<String?> _ref(ViewedPicture p) async {
    if (p.fileRef != null) return p.fileRef;
    final name = await ColliderApi.instance.download(p.url);
    return name == null ? null : 'downloaded/$name';
  }

  void _open(List<_Item> items, int i) {
    final pics = [
      for (final it in items)
        ViewedPicture(
          id: it.id,
          url: it.url,
          aspect: it.aspect,
          fileRef: it.fileRef,
          builder: it.theme == null
              ? null
              : (fit) => Image(image: _poster(it.theme!.assetPath), fit: fit, filterQuality: FilterQuality.high, gaplessPlayback: true),
        ),
    ];
    showGeneralDialog(
      context: context,
      barrierColor: Colors.transparent,
      pageBuilder: (ctx, _, __) => PictureViewer(
        pictures: pics,
        start: i,
        saved: _saved,
        onSave: _save,
        onFiles: (p) async {
          if (p.fileRef == null) await ColliderApi.instance.download(p.url);
        },
        onRemix: (p) async {
          final ref = await _ref(p);
          if (ref == null) return;
          if (ctx.mounted) Navigator.of(ctx).pop();
          widget.onRemix(ref);
        },
        onClose: () => Navigator.of(ctx).pop(),
      ),
    );
  }

  void _send() {
    final t = _text.text.trim();
    if (t.isEmpty) return;
    Drafts.sent('discover');
    widget.onImagine(t);
  }

  static ImageProvider _poster(String path) => path.startsWith('http') ? NetworkImage(path) as ImageProvider : AssetImage(path);

  Widget _buildGrid(List<_Item> items, double width, bool phone) {
    if (items.isEmpty) {
      return Center(
        child: Text(
          widget.view == 'gallery' ? 'No saved creations in My Gallery yet.' : 'Loading Discover Market...',
          style: VType.callout(color: VColors.textSecondary),
        ),
      );
    }
    final cols = width >= 1000 ? 4 : (width >= 600 ? 3 : 2);
    const gap = 4.0;
    final colW = (width - gap * (cols - 1)) / cols;
    final px = (colW * MediaQuery.devicePixelRatioOf(context)).round().clamp(240, 720);
    return GridView.builder(
      physics: const BouncingScrollPhysics(),
      padding: EdgeInsets.only(top: phone ? 56 : 64, bottom: 104, left: 4, right: 4),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: cols,
        mainAxisSpacing: gap,
        crossAxisSpacing: gap,
        childAspectRatio: 1168 / 1728,
      ),
      itemCount: items.length,
      itemBuilder: (context, index) {
        final it = items[index];
        final isSaved = _saved.contains(it.id);
        return VPress(
          onTap: () => _open(items, index),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: Stack(
              fit: StackFit.expand,
              children: [
                it.theme != null
                    ? Image(
                        image: ResizeImage(_poster(it.theme!.assetPath), width: px, policy: ResizeImagePolicy.fit),
                        fit: BoxFit.cover,
                        filterQuality: FilterQuality.medium,
                        gaplessPlayback: true,
                        frameBuilder: (_, child, frame, sync) => frame == null && !sync ? const BreathingTile() : child,
                        errorBuilder: (_, __, ___) => const ColoredBox(color: Color(0xFF0B0B0D)),
                      )
                    : Image.network(
                        it.url,
                        fit: BoxFit.cover,
                        filterQuality: FilterQuality.medium,
                        gaplessPlayback: true,
                        cacheWidth: px,
                        frameBuilder: (_, child, frame, sync) => frame == null && !sync ? const BreathingTile() : child,
                        errorBuilder: (_, __, ___) => const ColoredBox(color: Color(0xFF0B0B0D)),
                      ),
                Positioned(
                  left: 0,
                  right: 0,
                  bottom: 0,
                  height: 52,
                  child: DecoratedBox(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.bottomCenter,
                        end: Alignment.topCenter,
                        colors: [Colors.black.withValues(alpha: 0.78), Colors.transparent],
                      ),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.fromLTRB(10, 14, 10, 8),
                      child: Row(
                        children: [
                          Expanded(
                            child: Text(
                              it.title,
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: VType.caption(color: const Color(0xEBFFFFFF), weight: FontWeight.w500).copyWith(fontSize: 11),
                            ),
                          ),
                          if (isSaved)
                            const Padding(
                              padding: EdgeInsets.only(left: 4),
                              child: Icon(CupertinoIcons.heart_fill, size: 13, color: Color(0xFFFF375F)),
                            ),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.sizeOf(context);
    final phone = size.width < 768;
    final items = _items;
    return Stack(children: [
      Positioned.fill(
        child: GestureDetector(behavior: HitTestBehavior.opaque, onTap: widget.onClose, child: const ColoredBox(color: Color(0xE6000000))),
      ),
      SafeArea(
        bottom: false,
        child: Padding(
          padding: EdgeInsets.fromLTRB(0, phone ? 0 : 8, 0, phone ? 0 : 8),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 1100),
              child: ClipRRect(
                borderRadius: phone
                    ? const BorderRadius.vertical(bottom: Radius.circular(VRadius.xl))
                    : BorderRadius.circular(VRadius.xl),
                child: ColoredBox(
                  color: Colors.black,
                  child: LayoutBuilder(builder: (context, box) {
                    return Stack(children: [
                      Positioned.fill(
                        child: _buildGrid(items, box.maxWidth, phone),
                      ),
                      Positioned(
                        left: 0,
                        right: 0,
                        top: 0,
                        height: 68,
                        child: IgnorePointer(
                          child: DecoratedBox(
                            decoration: BoxDecoration(
                              gradient: LinearGradient(
                                begin: Alignment.topCenter,
                                end: Alignment.bottomCenter,
                                colors: [Colors.black.withValues(alpha: 0.88), Colors.black.withValues(alpha: 0.45), Colors.transparent],
                              ),
                            ),
                          ),
                        ),
                      ),
                      Positioned(
                        left: 12,
                        top: 10,
                        right: 12,
                        child: Row(children: [
                          VCircleButton(icon: Icons.close_rounded, tooltip: 'Close', floating: true, onTap: widget.onClose),
                          const SizedBox(width: 10),
                          Text(
                            widget.view == 'gallery' ? 'My Gallery' : 'Discover Market',
                            style: VType.headline(color: Colors.white),
                          ),
                          const Spacer(),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                            decoration: BoxDecoration(
                              color: const Color(0x28FFFFFF),
                              borderRadius: BorderRadius.circular(VRadius.full),
                            ),
                            child: Text(
                              '${items.length} items',
                              style: VType.caption(color: VColors.textSecondary, weight: FontWeight.w500),
                            ),
                          ),
                        ]),
                      ),
                      Positioned(
                        left: 0,
                        right: 0,
                        bottom: 0,
                        height: 104,
                        child: IgnorePointer(
                          child: DecoratedBox(
                            decoration: BoxDecoration(
                              gradient: LinearGradient(
                                begin: Alignment.bottomCenter,
                                end: Alignment.topCenter,
                                colors: [Colors.black.withValues(alpha: 0.92), Colors.black.withValues(alpha: 0.52), Colors.transparent],
                              ),
                            ),
                          ),
                        ),
                      ),
                      Positioned(
                        left: phone ? 76 : 16,
                        right: 16,
                        bottom: 12,
                        child: VGlass(
                          material: VMaterial.elevated,
                          radius: 26,
                          padding: const EdgeInsets.fromLTRB(16, 4, 6, 4),
                          child: Row(children: [
                            const Icon(CupertinoIcons.sparkles, size: 16, color: VColors.textSecondary),
                            const SizedBox(width: 10),
                            Expanded(
                              child: TextField(
                                controller: _text,
                                minLines: 1,
                                maxLines: 3,
                                cursorColor: VColors.textPrimary,
                                textInputAction: TextInputAction.send,
                                onSubmitted: (_) => _send(),
                                style: VType.callout(weight: FontWeight.w500),
                                decoration: InputDecoration(
                                  hintText: 'Describe an image to imagine or remix...',
                                  hintStyle: VType.callout(color: const Color(0x99FFFFFF), weight: FontWeight.w400),
                                  border: InputBorder.none,
                                  isDense: true,
                                  contentPadding: const EdgeInsets.symmetric(vertical: 10),
                                ),
                              ),
                            ),
                            const SizedBox(width: 6),
                            VCircleButton(icon: Icons.arrow_upward_rounded, size: 34, selected: true, onTap: _send),
                          ]),
                        ),
                      ),
                    ]);
                  }),
                ),
              ),
            ),
          ),
        ),
      ),
    ]);
  }
}
