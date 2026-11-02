// Files — Nimo Spatial OS file browser + ambient music library.
import '../../../core/drafts.dart';
import 'package:file_picker/file_picker.dart';
import 'package:material_ui/material_ui.dart';
import 'package:flutter/services.dart';
import 'dart:math' as math;
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import '../../../core/api/collider_api.dart';
import '../../../core/audio/generated_songs.dart';
import '../../../core/audio/music_player.dart';
import '../../../core/media/theme_cloud.dart';
import '../../../core/media/video_window.dart';
import '../../../core/platform/open_url.dart';
import '../../../core/vision/vision_kit.dart';
import '../../../models/theme_def.dart';
import '../../theme/theme_pack_store.dart';

class _N {
  static const titleBar = VColors.glassResting;
  static const body = Color(0x00000000);
  static const card = VColors.fillCell;
  static const chip = VColors.fillCell;
  static const chipOn = VColors.fillActive;
  static const title = VColors.textPrimary;
  static const label = VColors.textSecondary;
  static const count = VColors.textTertiary;
  static const hint = VColors.textTertiary;

  static TextStyle text(double size, FontWeight w, Color c, {double? height}) =>
      GoogleFonts.inter(fontSize: size, fontWeight: w, color: c, height: height, decoration: TextDecoration.none);
}

class _Source {
  final String key;
  final String label;
  final IconData icon;
  final List<Color> colors;
  const _Source(this.key, this.label, this.icon, this.colors);
}

const _home = _Source('home', 'Home', Icons.home_rounded, [Color(0xFF5CA194), Color(0xFF5BC7B1)]);
const _sources = [
  _Source('uploaded', 'Uploaded', Icons.upload_rounded, [Color(0xFF338C97), Color(0xFF4AC3DA)]),
  _Source('generated', 'Generated', Icons.article_rounded, [Color(0xFF2E5FC1), Color(0xFF6489DF)]),
  _Source('purchased', 'Purchased', Icons.shopping_bag_rounded, [Color(0xFF7C56C7), Color(0xFFAF83DF)]),
  _Source('downloaded', 'Downloaded', Icons.download_rounded, [Color(0xFF2C9472), Color(0xFF2EC68E)]),
];

const _kinds = [
  _Source('documents', 'Documents', Icons.insert_drive_file_rounded, [Color(0xFF338C97), Color(0xFF4AC3DA)]),
  _Source('images', 'Images', Icons.image_rounded, [Color(0xFF2E5FC1), Color(0xFF6489DF)]),
  _Source('music', 'Music', Icons.music_note_rounded, [Color(0xFFD65983), Color(0xFFD8789F)]),
  _Source('videos', 'Videos', Icons.videocam_rounded, [Color(0xFF7C56C7), Color(0xFFAF83DF)]),
];
_Source _sourceOf(String key) => [..._sources, ..._kinds].firstWhere((s) => s.key == key, orElse: () => _home);

bool _isKind(String place, ColliderFile f) => switch (place) {
      'images' => f.kind == 'image',
      'music' => f.kind == 'audio',
      'videos' => f.kind == 'video',
      'documents' => f.kind != 'image' && f.kind != 'audio' && f.kind != 'video',
      _ => true,
    };

class _View {
  final String source;
  final String? kind;
  final String? model;
  final ColliderFile? file;
  const _View(this.source, {this.kind, this.model, this.file});

  static _View start(String place) => _kinds.any((k) => k.key == place) ? _View('home', kind: place) : _View(place);

  bool same(_View o) => o.source == source && o.kind == kind && o.model == model && o.file == null && file == null;
}

class FilesScreen extends StatefulWidget {
  final VoidCallback onClose;
  final String initialPlace;
  final void Function(String url, String name)? onOpenDocument;
  const FilesScreen({super.key, required this.onClose, this.initialPlace = 'home', this.onOpenDocument});

  @override
  State<FilesScreen> createState() => _FilesScreenState();
}

class _FilesScreenState extends State<FilesScreen> {
  final _api = ColliderApi.instance;
  final TextEditingController _search = Drafts.text('files.search');
  Map<String, List<ColliderFile>> _files = {for (final s in _sources) s.key: const []};
  late final List<_View> _history = [_View.start(widget.initialPlace)];

  final Map<ColliderFile, (WallpaperTheme, int)> _songs = {};
  int _at = 0;
  bool _grid = true;
  bool _byName = false;
  String _q = '';
  bool _uploading = false;

  double _u = 0.62;

  _View get _view => _history[_at];

  bool get _songsOnly => _view.file == null && (_view.kind == 'music' || _view.source == 'purchased');

  @override
  void initState() {
    super.initState();
    ThemeCloud.instance.addListener(_onThemesChanged);
    ThemeCloud.instance.init();
    _populateSync();
    _load();
  }

  @override
  void dispose() {
    ThemeCloud.instance.removeListener(_onThemesChanged);
    super.dispose();
  }

  void _onThemesChanged() {
    if (!mounted) return;
    setState(() {
      _files = {
        ..._files,
        'purchased': _buildPurchased(),
      };
    });
  }

  List<ColliderFile> _buildPurchased() {
    final owned = ThemePackStore.instance.unlocked;
    final bypass = ThemePackStore.instance.bypass;
    final never = DateTime.fromMillisecondsSinceEpoch(0);
    final purchased = <ColliderFile>[];
    final seenTrackUrls = <String>{};
    _songs.clear();

    // Include free built-in themes + unlocked/bypassed cloud themes so Music & Purchased always have playable tracks
    final allThemes = <WallpaperTheme>[
      ...WallpaperCatalog.freeThemes,
      ...ThemeCloud.instance.themes,
    ];
    for (final t in allThemes) {
      if (!bypass && !owned.contains(t.id) && t.priceLabel != null) continue;
      final songs = MusicPlayer.forTheme(t);
      for (int i = 0; i < songs.length; i++) {
        final trackKey = '${songs[i].title.toLowerCase()}|${songs[i].file}';
        if (!seenTrackUrls.add(trackKey)) continue;
        final f = ColliderFile(songs[i].title, 'purchased', 0, never, 'audio', songs[i].file, asset: true);
        purchased.add(f);
        _songs[f] = (t, i);
      }
    }
    return purchased;
  }

  void _populateSync() {
    final cached = _api.cachedFiles;
    final purchased = _buildPurchased();
    _files = {
      'uploaded': cached?['uploaded'] ?? const [],
      'generated': cached?['generated'] ?? const [],
      'purchased': purchased,
      'downloaded': cached?['downloaded'] ?? const [],
    };
  }

  Future<void> _load({bool forceRefresh = false}) async {
    final server = await _api.files(forceRefresh: forceRefresh);
    await ThemePackStore.instance.init();
    final purchased = _buildPurchased();
    if (!mounted) return;
    setState(() => _files = {
          'uploaded': server['uploaded'] ?? const [],
          'generated': server['generated'] ?? const [],
          'purchased': purchased,
          'downloaded': server['downloaded'] ?? const [],
        });
  }

  void _open(ColliderFile f) => _go(_View(_view.source, kind: _view.kind, model: _view.model, file: f));

  void _go(_View v) {
    final song = v.file == null ? null : _songs[v.file!];
    if (song != null) {
      MusicPlayer.instance.play(song.$2, list: MusicPlayer.forTheme(song.$1), id: song.$1.id);
      return;
    }
    final f = v.file;
    if (f != null &&
        !f.asset &&
        widget.onOpenDocument != null &&
        RegExp(r'\.(docx|pdf|md|markdown|html?|txt)$', caseSensitive: false).hasMatch(f.name)) {
      widget.onOpenDocument!(f.url, f.name);
      return;
    }
    if (f != null && !f.asset && f.kind == 'audio' && f.source == 'generated') {
      if (_view.kind != 'music') {
        setState(() {
          _history.removeRange(_at + 1, _history.length);
          _history.add(_View(_view.source, kind: 'music', model: _view.model));
          _at++;
        });
      }
      GeneratedSongs.instance.toggle(_api.fileUrl(f));
      return;
    }
    setState(() {
      _history.removeRange(_at + 1, _history.length);
      _history.add(v);
      _at++;
    });
    if (f != null && !f.asset && _outside(f)) _appPicker(f);
  }

  bool _outside(ColliderFile f) => f.kind != 'image' && f.kind != 'video' && f.kind != 'text';

  final Map<String, List<int>> _bytes = {};

  Future<void> _appPicker(ColliderFile f) async {
    if (onThisComputer) {
      await _api.openWith(f);
      return;
    }
    final bytes = _bytes[f.url] ??= (await _api.fileBytes(f)) ?? const [];
    if (bytes.isEmpty) return;
    if (!await shareFile(bytes, f.name, _mime(f.name))) openUrl(_api.fileUrl(f));
  }

  static String _mime(String name) {
    final e = name.contains('.') ? name.split('.').last.toLowerCase() : '';
    return const {
          'mp3': 'audio/mpeg',
          'm4a': 'audio/mp4',
          'aac': 'audio/aac',
          'wav': 'audio/wav',
          'flac': 'audio/flac',
          'ogg': 'audio/ogg',
          'zip': 'application/zip',
          'csv': 'text/csv',
          'json': 'application/json',
          'stl': 'model/stl',
          'obj': 'model/obj',
          'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
          'svg': 'image/svg+xml',
          'exe': 'application/vnd.microsoft.portable-executable',
        }[e] ??
        'application/octet-stream';
  }

  Future<void> _upload() async {
    try {
      final res = await FilePicker.platform.pickFiles(allowMultiple: true, withData: true);
      if (res == null) return;
      setState(() => _uploading = true);
      for (final f in res.files) {
        if (f.bytes != null) await _api.uploadFile(f.name, f.bytes!);
      }
      await _load(forceRefresh: true);
    } catch (_) {
    } finally {
      if (mounted) setState(() => _uploading = false);
    }
  }

  List<String> get _models =>
      {for (final f in _files['generated'] ?? const <ColliderFile>[]) if (f.model.isNotEmpty) f.model}.toList()..sort();

  List<ColliderFile> _shown() {
    final v = _view;
    final all = [for (final s in _sources) ...?_files[s.key]];
    var list = v.source == 'home' ? all : [...?_files[v.source]];
    if (v.kind != null) list = list.where((f) => _isKind(v.kind!, f)).toList();
    if (v.source == 'generated' && v.model != null) list = list.where((f) => f.model == v.model).toList();
    if (_q.isNotEmpty) list = list.where((f) => f.name.toLowerCase().contains(_q)).toList();
    if (_byName) {
      list.sort((a, b) => a.name.toLowerCase().compareTo(b.name.toLowerCase()));
    } else {
      final order = {for (int i = 0; i < list.length; i++) list[i]: i};
      list.sort((a, b) {
        final c = b.modified.compareTo(a.modified);
        return c != 0 ? c : order[a]!.compareTo(order[b]!);
      });
    }
    return list;
  }

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;
    final compact = size.width < 768;
    return LayoutBuilder(builder: (context, box) {
      const railW = 46.0;
      const railGap = 10.0;
      final winW = compact
          ? (box.maxWidth - 32 - railW - railGap).clamp(260.0, 640.0)
          : (box.maxWidth - 140).clamp(460.0, 880.0);
      _u = compact ? (winW / 576).clamp(0.48, 0.65) : 0.64;
      final winH = compact ? size.height * 0.62 : (box.maxHeight * 0.78).clamp(400.0, 640.0);
      return GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: widget.onClose,
        child: Align(
          alignment: Alignment.center,
          child: TweenAnimationBuilder<double>(
            tween: Tween(begin: 0, end: 1),
            duration: const Duration(milliseconds: 240),
            curve: Curves.easeOutCubic,
            builder: (_, t, child) => Opacity(opacity: t, child: Transform.scale(scale: 0.96 + 0.04 * t, child: child)),
            child: GestureDetector(
              onTap: () {},
              child: SizedBox(
                width: winW + railW + railGap,
                height: winH,
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    _sideMenu(),
                    const SizedBox(width: railGap),
                    Expanded(
                      child: SizedBox(
                        height: winH,
                        child: _window(compact),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      );
    });
  }

  Widget _window(bool compact) {
    return VGlass(
      material: VMaterial.work,
      radius: 22,
      child: Column(
        children: [
          _titleBar(compact),
          Expanded(
            child: Container(
              width: double.infinity,
              color: _N.body,
              child: AnimatedSwitcher(
                duration: const Duration(milliseconds: 200),
                child: KeyedSubtree(
                  key: ValueKey('${_view.source}|${_view.kind}|${_view.model}|${_view.file?.url}|${_grid && !_songsOnly}'),
                  child: _view.file != null ? _preview(_view.file!) : _browse(),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _titleBar(bool compact) {
    final title = _view.file?.name ?? _sourceOf(_view.source == 'home' && _view.kind != null ? _view.kind! : _view.source).label;
    final nav = Row(mainAxisSize: MainAxisSize.min, children: [
      _RoundButton(icon: Icons.chevron_left_rounded, enabled: _at > 0, tooltip: 'Back', onTap: () => setState(() => _at--)),
      SizedBox(width: compact ? 4 : 6),
      _RoundButton(icon: Icons.chevron_right_rounded, enabled: _at < _history.length - 1, tooltip: 'Forward', onTap: () => setState(() => _at++)),
    ]);
    final actions = Row(mainAxisSize: MainAxisSize.min, children: [
      if (!_songsOnly) ...[
        _SquareButton(
          icon: _grid ? Icons.grid_view_rounded : Icons.view_list_rounded,
          on: true,
          tooltip: _grid ? 'Grid' : 'List',
          onTap: () => setState(() => _grid = !_grid),
        ),
        SizedBox(width: compact ? 4 : 6),
      ],
      _SquareButton(
        icon: Icons.swap_vert_rounded,
        on: _byName,
        tooltip: _byName ? 'By name' : 'Newest first',
        onTap: () => setState(() => _byName = !_byName),
      ),
      SizedBox(width: compact ? 4 : 6),
      _SquareButton(
        icon: _uploading ? Icons.more_horiz_rounded : Icons.upload_rounded,
        tooltip: 'Upload',
        onTap: _uploading ? null : _upload,
      ),
      SizedBox(width: compact ? 4 : 6),
      _SquareButton(icon: Icons.close_rounded, tooltip: 'Close', onTap: widget.onClose),
    ]);
    final search = VSearchField(
      controller: _search,
      hint: 'Search files & music...',
      onChanged: (v) => setState(() => _q = v.trim().toLowerCase()),
    );
    final name = Text(title, maxLines: 1, overflow: TextOverflow.ellipsis, style: _N.text(16, FontWeight.w600, _N.title));
    return Container(
      color: _N.titleBar,
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      child: compact
          ? Column(crossAxisAlignment: CrossAxisAlignment.start, mainAxisSize: MainAxisSize.min, children: [
              Row(children: [nav, const SizedBox(width: 8), Expanded(child: name), actions]),
              const SizedBox(height: 8),
              search,
            ])
          : Row(children: [
              Expanded(child: Row(children: [nav, const SizedBox(width: 12), Flexible(child: name)])),
              SizedBox(width: 240, child: search),
              Expanded(child: Align(alignment: Alignment.centerRight, child: actions)),
            ]),
    );
  }

  Widget _browse() {
    final home = _view.source == 'home';
    final list = _shown();
    return EdgeFade(
      focus: FadeFocus.top,
      child: ListView(
        padding: const EdgeInsets.fromLTRB(16, 14, 16, 28),
        physics: const BouncingScrollPhysics(),
        children: [
          if (home) ...[
            Row(children: [
              for (int i = 0; i < _sources.length; i++) ...[
                if (i > 0) const SizedBox(width: 10),
                Expanded(
                  child: _SourceCard(
                    source: _sources[i],
                    count: (_files[_sources[i].key] ?? const []).length,
                    onTap: () => _go(_View(_sources[i].key, kind: _view.kind)),
                  ),
                ),
              ],
            ]),
            const SizedBox(height: 16),
            if (list.isNotEmpty) ...[
              Container(height: 0.5, color: VColors.borderLight),
              const SizedBox(height: 14),
              Row(
                children: [
                  Text(
                    _view.kind != null ? _sourceOf(_view.kind!).label : 'Recents',
                    style: _N.text(15, FontWeight.w600, _N.title),
                  ),
                  const SizedBox(width: 8),
                  Text('${list.length} items', style: _N.text(11, FontWeight.w500, _N.hint)),
                ],
              ),
              const SizedBox(height: 12),
            ],
          ],
          if (_view.source == 'generated' && _models.isNotEmpty) ...[
            Wrap(spacing: 6, runSpacing: 6, children: [
              VChip(label: 'All', selected: _view.model == null, onTap: () => _go(_View('generated', kind: _view.kind))),
              for (final m in _models)
                VChip(label: m, selected: _view.model == m, onTap: () => _go(_View('generated', kind: _view.kind, model: m))),
            ]),
            const SizedBox(height: 14),
          ],
          if (list.isEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 48),
              child: Center(
                child: Text(
                  'No files in this view yet.',
                  style: _N.text(12, FontWeight.w500, _N.hint),
                ),
              ),
            )
          else if (_grid && !_songsOnly)
            LayoutBuilder(builder: (context, c) {
              final cols = ((c.maxWidth + 16) / 112).floor().clamp(3, 8);
              final w = c.maxWidth / cols;
              return Wrap(
                runSpacing: 18,
                children: [
                  for (final f in list)
                    SizedBox(
                      width: w,
                      child: _FileCell(
                        file: f,
                        api: _api,
                        onTap: () => _open(f),
                        onLongPress: f.asset ? null : () => _detail(f),
                      ),
                    ),
                ],
              );
            })
          else
            Column(children: [
              for (final f in list)
                if (_songs[f] case final song?)
                  _SongRow(title: f.name, theme: song.$1, index: song.$2, onTap: () => _open(f))
                else
                  _FileRow(file: f, api: _api, onTap: () => _open(f), onLongPress: f.asset ? null : () => _detail(f)),
            ]),
        ],
      ),
    );
  }

  Future<void> _send(ColliderFile f) async {
    final bytes = _bytes[f.url] ??= (await _api.fileBytes(f)) ?? const [];
    if (bytes.isNotEmpty && await shareFile(bytes, f.name, _mime(f.name))) return;
    if (!await shareText(_api.fileUrl(f))) await Clipboard.setData(ClipboardData(text: _api.fileUrl(f)));
  }

  void _detail(ColliderFile f) {
    final docs = RegExp(r'\.(docx|pdf|md|markdown|html?|txt)$', caseSensitive: false).hasMatch(f.name);
    showGeneralDialog(
      context: context,
      barrierColor: Colors.transparent,
      barrierDismissible: false,
      transitionDuration: Duration.zero,
      pageBuilder: (ctx, _, __) {
        void close() => Navigator.of(ctx).pop();
        final size = MediaQuery.sizeOf(ctx);
        final Widget content = switch (f.kind) {
          'image' => InteractiveViewer(
              minScale: 1,
              maxScale: 5,
              clipBehavior: Clip.none,
              child: DetailRaised(child: Image.network(_api.fileUrl(f), fit: BoxFit.contain, filterQuality: FilterQuality.high)),
            ),
          'text' => ConstrainedBox(
              constraints: BoxConstraints(maxHeight: DetailView.zoneHeight(ctx)),
              child: FutureBuilder<String>(
                future: _api.fileText(f),
                builder: (_, snap) => VFadeScroll(
                  fade: 30,
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 26),
                  child: SelectableText(
                    snap.data ?? '',
                    style: VType.body().copyWith(fontSize: 11, height: 1.5, shadows: const [Shadow(color: Color(0x99000000), blurRadius: 14)]),
                  ),
                ),
              ),
            ),
          _ => Column(mainAxisSize: MainAxisSize.min, children: [
              DetailRaised(radius: 12, child: _Thumb(file: f, api: _api, width: math.min(220.0, size.width * 0.5))),
              const SizedBox(height: 14),
              Text(
                f.name,
                textAlign: TextAlign.center,
                style: VType.callout().copyWith(shadows: const [Shadow(color: Color(0x99000000), blurRadius: 12)]),
              ),
            ]),
        };
        return DetailView(
          onClose: close,
          onSend: () => _send(f),
          onOpen: () => _appPicker(f),
          actions: [
            if (f.kind == 'audio' || f.kind == 'video')
              DetailAction(Icons.play_arrow_rounded, 'Play', () {
                close();
                _open(f);
              }),
            if (docs && widget.onOpenDocument != null)
              DetailAction(Icons.edit_rounded, 'Edit', () {
                close();
                widget.onOpenDocument!(f.url, f.name);
              }),
          ],
          child: content,
        );
      },
    );
  }

  Widget _preview(ColliderFile f) {
    if (f.kind == 'audio') return Center(child: _Thumb(file: f, api: _api, width: 180));
    if (f.kind == 'video' && !f.asset) {
      return VideoWindow(key: ValueKey(f.url), url: _api.fileUrl(f), onClose: () => setState(() => _at--));
    }
    if (f.kind == 'image') {
      return Padding(
        padding: const EdgeInsets.all(14),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(12),
          child: f.asset ? Image.asset(f.url, fit: BoxFit.contain) : Image.network(_api.fileUrl(f), fit: BoxFit.contain),
        ),
      );
    }
    if (f.kind == 'text') {
      return FutureBuilder<String>(
        future: _api.fileText(f),
        builder: (_, snap) => SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          physics: const BouncingScrollPhysics(),
          child: SelectableText(snap.data ?? '', style: _N.text(11, FontWeight.w400, _N.label, height: 1.5)),
        ),
      );
    }
    return Center(
      child: Column(mainAxisSize: MainAxisSize.min, children: [
        _Thumb(file: f, api: _api, width: 96),
        const SizedBox(height: 14),
        VPress(
          onTap: () => _appPicker(f),
          child: Container(
            height: 36,
            padding: const EdgeInsets.symmetric(horizontal: 16),
            decoration: BoxDecoration(color: _N.chipOn, borderRadius: BorderRadius.circular(12)),
            child: Row(mainAxisSize: MainAxisSize.min, children: [
              const Icon(Icons.open_in_new_rounded, size: 16, color: Colors.white),
              const SizedBox(width: 8),
              Text('Open', style: _N.text(11, FontWeight.w600, Colors.white)),
            ]),
          ),
        ),
      ]),
    );
  }

  Widget _sideMenu() {
    return SizedBox(
      width: 46,
      child: VGlass(
        material: VMaterial.elevated,
        radius: 23,
        padding: const EdgeInsets.symmetric(vertical: 12),
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          for (final s in [_home, ..._kinds]) ...[
            if (s.key != 'home') const SizedBox(height: 10),
            VPress(
              tooltip: s.label,
              onTap: () {
                final next = s.key == 'home'
                    ? const _View('home')
                    : _View(_view.source, kind: _view.kind == s.key ? null : s.key, model: _view.model);
                if (!next.same(_view)) _go(next);
              },
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 180),
                width: 32,
                height: 32,
                decoration: BoxDecoration(
                  color: (s.key == 'home' ? _view.source == 'home' && _view.kind == null : _view.kind == s.key)
                      ? _N.chipOn
                      : Colors.transparent,
                  shape: BoxShape.circle,
                ),
                child: Center(child: _GradientIcon(s.icon, s.colors, 18)),
              ),
            ),
          ],
        ]),
      ),
    );
  }
}

class _GradientIcon extends StatelessWidget {
  final IconData icon;
  final List<Color> colors;
  final double size;
  const _GradientIcon(this.icon, this.colors, this.size);

  @override
  Widget build(BuildContext context) => ShaderMask(
        blendMode: BlendMode.srcIn,
        shaderCallback: (r) => LinearGradient(begin: Alignment.topCenter, end: Alignment.bottomCenter, colors: colors).createShader(r),
        child: Icon(icon, size: size, color: Colors.white),
      );
}

class _RoundButton extends StatelessWidget {
  final IconData icon;
  final bool enabled;
  final String tooltip;
  final VoidCallback onTap;
  const _RoundButton({required this.icon, required this.enabled, required this.tooltip, required this.onTap});

  @override
  Widget build(BuildContext context) => VPress(
        tooltip: tooltip,
        onTap: enabled ? onTap : null,
        child: Container(
          width: 30,
          height: 30,
          decoration: const BoxDecoration(color: _N.chip, shape: BoxShape.circle),
          child: Icon(icon, size: 20, color: enabled ? _N.title : _N.count),
        ),
      );
}

class _SquareButton extends StatelessWidget {
  final IconData icon;
  final bool on;
  final String tooltip;
  final VoidCallback? onTap;
  const _SquareButton({required this.icon, required this.tooltip, required this.onTap, this.on = false});

  @override
  Widget build(BuildContext context) => VPress(
        tooltip: tooltip,
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 160),
          width: 30,
          height: 30,
          decoration: BoxDecoration(color: on ? _N.chipOn : _N.chip, borderRadius: BorderRadius.circular(11)),
          child: Icon(icon, size: 17, color: on ? Colors.white : _N.title),
        ),
      );
}

class _SourceCard extends StatelessWidget {
  final _Source source;
  final int count;
  final VoidCallback onTap;
  const _SourceCard({required this.source, required this.count, required this.onTap});

  @override
  Widget build(BuildContext context) => VPress(
        onTap: onTap,
        child: Container(
          height: 68,
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
          decoration: BoxDecoration(
            color: _N.card,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: VColors.borderSubtle, width: 0.5),
            boxShadow: VShadow.subtle,
          ),
          child: Row(
            children: [
              Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  color: source.colors.first.withValues(alpha: 0.18),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Center(child: _GradientIcon(source.icon, source.colors, 20)),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      source.label,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: _N.text(11.5, FontWeight.w600, _N.title),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      '$count ${count == 1 ? 'item' : 'items'}',
                      maxLines: 1,
                      style: _N.text(10, FontWeight.w500, _N.hint),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      );
}

class _Thumb extends StatelessWidget {
  final ColliderFile file;
  final ColliderApi api;
  final double width;
  const _Thumb({required this.file, required this.api, required this.width});

  static const _word = (Icons.description_rounded, [Color(0xFF6CC8FF), Color(0xFF0A63F0)]);
  static const _pdf = (Icons.picture_as_pdf_rounded, [Color(0xFFFF7A70), Color(0xFFE0221B)]);
  static const _note = (Icons.notes_rounded, [Color(0xFFD1D1D6), Color(0xFF8E8E93)]);
  static const _web = (Icons.html_rounded, [Color(0xFFFFB15C), Color(0xFFFF6A00)]);
  static const _code = (Icons.code_rounded, [Color(0xFF46E6CF), Color(0xFF0087A8)]);
  static const _data = (Icons.data_object_rounded, [Color(0xFFFFD95A), Color(0xFFFF9F0A)]);
  static const _sheet = (Icons.table_chart_rounded, [Color(0xFF9BE564), Color(0xFF22A84A)]);
  static const _slides = (Icons.slideshow_rounded, [Color(0xFFFFAA4D), Color(0xFFFF2D6A)]);
  static const _zip = (Icons.folder_zip_rounded, [Color(0xFFD2A679), Color(0xFF8B5E3C)]);
  static const _app = (Icons.install_desktop_rounded, [Color(0xFF8A93FF), Color(0xFF4C36D6)]);
  static const _song = (Icons.music_note_rounded, [Color(0xFFFF7A95), Color(0xFFD0105C)]);
  static const _film = (Icons.movie_rounded, [Color(0xFFE26BFF), Color(0xFF6E34E8)]);
  static const _picture = (Icons.image_rounded, [Color(0xFFFFD95A), Color(0xFFFF8A00)]);
  static const _other = (Icons.insert_drive_file_rounded, [Color(0xFFD1D1D6), Color(0xFF8E8E93)]);
  static const _byEnding = {
    'docx': _word,
    'doc': _word,
    'rtf': _word,
    'odt': _word,
    'pages': _word,
    'pdf': _pdf,
    'md': _note,
    'markdown': _note,
    'txt': _note,
    'log': _note,
    'html': _web,
    'htm': _web,
    'py': _code,
    'dart': _code,
    'js': _code,
    'ts': _code,
    'css': _code,
    'sh': _code,
    'bat': _code,
    'ps1': _code,
    'c': _code,
    'cpp': _code,
    'h': _code,
    'java': _code,
    'go': _code,
    'rs': _code,
    'sql': _code,
    'json': _data,
    'xml': _data,
    'yaml': _data,
    'yml': _data,
    'toml': _data,
    'ini': _data,
    'csv': _sheet,
    'xlsx': _sheet,
    'xls': _sheet,
    'ods': _sheet,
    'numbers': _sheet,
    'pptx': _slides,
    'ppt': _slides,
    'key': _slides,
    'odp': _slides,
    'zip': _zip,
    '7z': _zip,
    'rar': _zip,
    'gz': _zip,
    'tar': _zip,
    'exe': _app,
    'msi': _app,
    'apk': _app,
    'dmg': _app,
  };
  static (IconData, List<Color>) iconFor(ColliderFile f) {
    final dot = f.name.lastIndexOf('.');
    final ending = dot < 0 ? '' : f.name.substring(dot + 1).toLowerCase();
    return _byEnding[ending] ??
        switch (f.kind) {
          'audio' => _song,
          'video' => _film,
          'image' => _picture,
          'pdf' => _pdf,
          'text' => _note,
          _ => _other,
        };
  }

  @override
  Widget build(BuildContext context) {
    final h = width;
    Widget tile() {
      final (icon, colors) = iconFor(file);
      return Container(
        decoration: BoxDecoration(gradient: LinearGradient(begin: Alignment.topCenter, end: Alignment.bottomCenter, colors: colors)),
        child: Center(
          child: Icon(
            icon,
            size: h * 0.46,
            color: Colors.white,
            shadows: const [Shadow(color: Color(0x40000000), blurRadius: 6, offset: Offset(0, 2))],
          ),
        ),
      );
    }

    return ClipRRect(
      borderRadius: BorderRadius.circular(10),
      child: SizedBox(
        width: width,
        height: h,
        child: file.asset
            ? (file.kind == 'image' ? Image.asset(file.url, fit: BoxFit.cover, errorBuilder: (_, __, ___) => tile()) : tile())
            : Image.network(
                api.thumbUrl(file),
                fit: (file.kind == 'image' && !file.name.toLowerCase().endsWith('.svg')) || file.kind == 'video'
                    ? BoxFit.cover
                    : BoxFit.contain,
                filterQuality: FilterQuality.high,
                frameBuilder: (_, child, frame, sync) => frame == null && !sync
                    ? tile()
                    : (file.kind == 'image' || file.kind == 'video' ? child : ColoredBox(color: const Color(0x14FFFFFF), child: child)),
                errorBuilder: (_, __, ___) => tile(),
              ),
      ),
    );
  }
}

class _FileCell extends StatelessWidget {
  final ColliderFile file;
  final ColliderApi api;
  final VoidCallback onTap;
  final VoidCallback? onLongPress;
  const _FileCell({required this.file, required this.api, required this.onTap, this.onLongPress});

  List<Widget> _name() {
    final dot = file.name.lastIndexOf('.');
    final hasEnding = dot > 0 && file.name.length - dot <= 6;
    final style = _N.text(11, FontWeight.w400, _N.label, height: 1.27);
    return [
      Text(
        hasEnding ? file.name.substring(0, dot) : file.name,
        maxLines: hasEnding ? 1 : 2,
        overflow: TextOverflow.ellipsis,
        textAlign: TextAlign.center,
        style: style,
      ),
      if (hasEnding) Text(file.name.substring(dot), maxLines: 1, style: style),
    ];
  }

  @override
  Widget build(BuildContext context) => GestureDetector(
        onLongPress: onLongPress,
        child: VPress(
          onTap: onTap,
          tooltip: file.name,
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 6),
            child: Column(mainAxisSize: MainAxisSize.min, children: [
              file.kind == 'audio' && file.source == 'generated'
                  ? _SongState(url: api.fileUrl(file), child: _Thumb(file: file, api: api, width: 84))
                  : _Thumb(file: file, api: api, width: 84),
              const SizedBox(height: 8),
              ..._name(),
            ]),
          ),
        ),
      );
}

class _SongRow extends StatelessWidget {
  final String title;
  final WallpaperTheme theme;
  final int index;
  final VoidCallback onTap;
  const _SongRow({required this.title, required this.theme, required this.index, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final p = MusicPlayer.instance;
    return AnimatedBuilder(
      animation: p,
      builder: (_, __) {
        final on = p.queueId == theme.id && p.index == index && p.playing;
        return VPress(
          onTap: onTap,
          child: Container(
            margin: const EdgeInsets.only(bottom: 4),
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
            decoration: BoxDecoration(
              color: on ? const Color(0x22D65983) : Colors.transparent,
              borderRadius: BorderRadius.circular(10),
            ),
            child: Row(children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(6),
                child: SizedBox(
                  width: 40,
                  height: 40,
                  child: theme.assetPath.startsWith('http')
                      ? Image.network(
                          theme.assetPath,
                          fit: BoxFit.cover,
                          filterQuality: FilterQuality.medium,
                          errorBuilder: (_, __, ___) => const ColoredBox(color: Color(0xFF282C34)),
                        )
                      : Image.asset(
                          theme.assetPath,
                          fit: BoxFit.cover,
                          filterQuality: FilterQuality.medium,
                          errorBuilder: (_, __, ___) => const ColoredBox(color: Color(0xFF282C34)),
                        ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text(
                    title,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: _N.text(11.5, FontWeight.w600, on ? const Color(0xFFFF7A95) : _N.title),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    theme.name.replaceAll(RegExp(r'\s*4K$'), '').trim(),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: _N.text(10.5, FontWeight.w500, _N.hint),
                  ),
                ]),
              ),
              Icon(
                on ? CupertinoIcons.pause_fill : CupertinoIcons.play_arrow_solid,
                size: 15,
                color: on ? const Color(0xFFFF7A95) : _N.hint,
              ),
              const SizedBox(width: 4),
            ]),
          ),
        );
      },
    );
  }
}

class _FileRow extends StatelessWidget {
  final ColliderFile file;
  final ColliderApi api;
  final VoidCallback onTap;
  final VoidCallback? onLongPress;
  const _FileRow({required this.file, required this.api, required this.onTap, this.onLongPress});

  static String _size(int b) {
    if (b <= 0) return '';
    if (b < 1024) return '$b B';
    if (b < 1024 * 1024) return '${(b / 1024).toStringAsFixed(1)} KB';
    return '${(b / 1024 / 1024).toStringAsFixed(1)} MB';
  }

  @override
  Widget build(BuildContext context) {
    final when = file.modified.millisecondsSinceEpoch == 0 ? '' : DateFormat('d MMM, HH:mm').format(file.modified);
    final meta = [file.model, _size(file.size), when].where((s) => s.isNotEmpty).join('  ·  ');
    return GestureDetector(
      onLongPress: onLongPress,
      child: VPress(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 6),
          child: Row(children: [
            file.kind == 'audio' && file.source == 'generated'
                ? _SongState(url: api.fileUrl(file), child: _Thumb(file: file, api: api, width: 44))
                : _Thumb(file: file, api: api, width: 44),
            const SizedBox(width: 10),
            Expanded(
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(file.name, maxLines: 1, overflow: TextOverflow.ellipsis, style: _N.text(11, FontWeight.w600, _N.label)),
                if (meta.isNotEmpty) ...[
                  const SizedBox(height: 2),
                  Text(meta, style: _N.text(11, FontWeight.w500, _N.hint)),
                ],
              ]),
            ),
          ]),
        ),
      ),
    );
  }
}

class _SongState extends StatelessWidget {
  final String url;
  final Widget child;
  const _SongState({required this.url, required this.child});

  @override
  Widget build(BuildContext context) {
    final s = GeneratedSongs.instance;
    return AnimatedBuilder(
      animation: s,
      builder: (_, __) {
        final on = s.isPlaying(url);
        final started = s.url == url && s.position > 0;
        return Stack(alignment: Alignment.center, children: [
          child,
          AnimatedOpacity(
            opacity: on ? 1 : 0,
            duration: const Duration(milliseconds: 220),
            child: Container(
              width: 30,
              height: 30,
              decoration: const BoxDecoration(color: Color(0x66000000), shape: BoxShape.circle),
              child: const Icon(Icons.pause_rounded, size: 20, color: Colors.white),
            ),
          ),
          if (started)
            Positioned(
              left: 6,
              right: 6,
              bottom: 6,
              child: ClipRRect(
                borderRadius: BorderRadius.circular(2),
                child: LinearProgressIndicator(
                  value: s.progressOf(url),
                  minHeight: 3,
                  backgroundColor: const Color(0x40FFFFFF),
                  valueColor: const AlwaysStoppedAnimation(Colors.white),
                ),
              ),
            ),
        ]);
      },
    );
  }
}
