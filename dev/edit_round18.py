# Made by Claude (2026-10-21). Round 18: the picture category of the chat (the media chat) and Discover's hand-off.
# David, 21 Oct: "either bring the chat window to discover or have discover spit us to media gen rather than duplicate
# value". Discover sends its words and its remixes here; the picture models are the Image category of the chat, with
# their toolbar, queue and generations pane (lib/features/media/generations_pane.dart).
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


API = "lib/core/api/collider_api.dart"
edit(API, [
    ("""  final String? from; // for a video made from a picture: the making that holds the picture
  const Creation(this.id, this.kind, this.text, this.status, this.media, [this.from]);""",
     """  final String? from; // for a video made from a picture: the making that holds the picture
  final String model; // "Provider:model" asked for, '' for the configuration's order
  final String label; // the model that made it, by name
  final List<String> references; // pictures it was made from, as "source/name" in Files
  final String aspect;
  final int count;
  const Creation(this.id, this.kind, this.text, this.status, this.media,
      [this.from, this.model = '', this.label = '', this.references = const [], this.aspect = '', this.count = 0]);"""),
    ("""        j['from'] == null ? null : '${j['from']}',
      );
  bool get making => status == 'making';""",
     """        j['from'] == null ? null : '${j['from']}',
        '${j['model'] ?? ''}',
        '${j['label'] ?? ''}',
        [for (final r in (j['references'] as List? ?? const [])) '$r'],
        '${j['aspect'] ?? ''}',
        (j['count'] as num?)?.toInt() ?? 0,
      );
  bool get making => status == 'making';"""),
    ("""  Future<void> make(String text, String kind, {String? from, String? replace}) async {
    try {
      await _dio.post('$_base/api/imagine',
          data: {'text': text, 'kind': kind, if (from != null) 'from': from, if (replace != null) 'replace': replace});""",
     """  Future<void> make(String text, String kind,
      {String? from, String? replace, String? model, List<String>? references, String? aspect, int? count}) async {
    try {
      await _dio.post('$_base/api/imagine', data: {
        'text': text,
        'kind': kind,
        if (from != null) 'from': from,
        if (replace != null) 'replace': replace,
        if (model != null) 'model': model,
        if (references != null && references.isNotEmpty) 'references': references,
        if (aspect != null) 'aspect': aspect,
        if (count != null) 'count': count,
      });"""),
    ("""      ModelRoster.setLive([
        for (final m in list)""", """      // The picture models (Claude, 2026-10-21): the Image category, from the providers that have keys.
      var pictures = const <Map>[];
      try {
        pictures = ((await _dio.get('$_base/api/imagine')).data['models'] as List? ?? const []).cast<Map>();
      } catch (_) {}
      ModelRoster.setLive([
        for (final m in pictures)
          ModelDef(
            id: '${m['id']}',
            label: '${m['label']}',
            short: '${m['label']}'.split(' ').map((w) => w.isEmpty ? '' : w[0]).join(),
            desc: '${m['provider']}',
            tier: ModelTier.free,
            categories: const [ModelCategory.image],
            providerColor: const Color(0xFF8E8E93),
            isMedia: true,
          ),
        for (final m in list)"""),
])

edit("lib/models/model_def.dart", [
    ("""  static List<ModelDef> allModels = List.of(_seed);""",
     """  static List<ModelDef> allModels = [for (final m in _seed) if (!m.isMedia) m];"""),
    ("""    allModels = [...live, ..._seed.where((m) => m.isMedia)];""",
     """    // The seed's media models were names with nothing behind them; the live picture models come from the server.
    allModels = [...live];"""),
])

edit("lib/features/nav/contextual_side_nav.dart", [
    ("""        if (ModelRoster.forCategory(c).any((m) => !m.isMedia)) c,""", """        if (ModelRoster.forCategory(c).isNotEmpty) c,"""),
    ("""    final models = ModelRoster.forCategory(cat).where((m) => !m.isMedia).toList();""",
     """    final models = ModelRoster.forCategory(cat);"""),
])

edit("lib/features/prompt/floating_prompt.dart", [
    ("""class _FloatingPromptState extends State<FloatingPrompt> {
  final TextEditingController _ctrl = TextEditingController();
  final FocusNode _focus = FocusNode();
  final List<String> _files = [];
  bool _options = false;
""", """class _FloatingPromptState extends State<FloatingPrompt> {
  final TextEditingController _ctrl = TextEditingController();
  final FocusNode _focus = FocusNode();
  final List<String> _files = [];
  bool _options = false;

  @override
  void initState() {
    super.initState();
    FloatingPrompt.attach.addListener(_attached);
  }

  /// A picture handed over (Discover's remix): it goes with the next message, as its reference.
  void _attached() {
    final f = FloatingPrompt.attach.value;
    if (f == null) return;
    FloatingPrompt.attach.value = null;
    if (mounted && !_files.contains(f)) setState(() => _files.add(f));
  }
"""),
    ("""  @override
  void dispose() {
    _ctrl.dispose();
    _focus.dispose();""", """  @override
  void dispose() {
    FloatingPrompt.attach.removeListener(_attached);
    _ctrl.dispose();
    _focus.dispose();"""),
    ("""class FloatingPrompt extends StatefulWidget {""", """class FloatingPrompt extends StatefulWidget {
  /// A file to add to the message being written (Claude, 2026-10-21): Discover's remix puts its picture here.
  static final ValueNotifier<String?> attach = ValueNotifier(null);
"""),
    ("""      for (final f in _files) VChip(label: f.length > 22 ? '${f.substring(0, 21)}…' : f, selected: true, onTap: () => setState(() => _files.remove(f))),""",
     """      for (final f in _files)
        VChip(
            label: () {
              final n = f.split('/').last;
              return n.length > 22 ? '${n.substring(0, 21)}…' : n;
            }(),
            selected: true,
            onTap: () => setState(() => _files.remove(f))),"""),
])

M = "lib/main.dart"
edit(M, [
    ("""import 'features/theme/theme_pack_store.dart';
""", """import 'features/theme/theme_pack_store.dart';
import 'features/media/generations_pane.dart';
"""),
    ("""  ModelCategory _activeCategory = ModelCategory.general;
""", """  ModelCategory _activeCategory = ModelCategory.general;
  // The Image category (Claude, 2026-10-21): the shape and number of pictures, and the generations pane.
  String _aspect = '9:16';
  int _count = 4;
  bool _mediaExpanded = false;
  int _mediaRefresh = 0;
"""),
    ("""        ..addAll(live.take(6));""", """        ..addAll(live.take(6))
        ..addAll(ModelRoster.forCategory(ModelCategory.image).take(1).map((m) => m.id));"""),
    ("""  Future<void> _onSendPrompt(String prompt, [List<String> files = const []]) async {
""", """  /// The Image category: the words (and any reference pictures) go to the picture models chosen there.
  Future<void> _onSendImage(String prompt, [List<String> files = const []]) async {
    var models = _selectedModelIds.where((id) => ModelRoster.byId(id)?.categories.contains(ModelCategory.image) ?? false).toList();
    if (models.isEmpty) models = ModelRoster.forCategory(ModelCategory.image).take(1).map((m) => m.id).toList();
    if (models.isEmpty) return;
    final refs = [for (final f in files) f.contains('/') ? f : 'uploaded/$f'];
    setState(() => _isComposerSummoned = false);
    for (final m in models) {
      await ColliderApi.instance.make(prompt, 'image', model: m, references: refs, aspect: _aspect, count: _count);
    }
    if (mounted) setState(() => _mediaRefresh++);
  }

  /// From Discover: to the chat's Image category, with words to make from, or a picture to remix (Grok's remix).
  void _toImageChat({String? text, String? reference}) {
    _requestSwitchSurface(null);
    setState(() {
      _activeCategory = ModelCategory.image;
      _isComposerSummoned = reference != null;
    });
    if (reference != null) FloatingPrompt.attach.value = reference;
    if (text != null) _onSendImage(text);
  }

  Future<void> _onSendPrompt(String prompt, [List<String> files = const []]) async {
    if (_activeCategory == ModelCategory.image) return _onSendImage(prompt, files);
"""),
    ("""                          maxWidth: isMobile
                              ? (openItem != null ? 300.0 : 260.0)
                              : (openItem != null ? 780.0 : 480.0),
                          // rows: never more than 40% of the screen; a conversation: "halfway up is sufficient"
                          maxHeight: MediaQuery.of(context).size.height * (openItem != null ? 0.50 : 0.40),""",
     """                          maxWidth: isMobile
                              ? (openItem != null || media ? 300.0 : 260.0)
                              : (openItem != null || media ? 780.0 : 480.0),
                          // rows: never more than 40% of the screen; a conversation: "halfway up is sufficient"
                          maxHeight: MediaQuery.of(context).size.height * (openItem != null || (media && _mediaExpanded) ? 0.50 : 0.40),"""),
    ("""                          child: openItem == null
                              ? rows""", """                          child: media
                              ? GenerationsPane(
                                  aspect: _aspect,
                                  count: _count,
                                  onAspect: (a) => setState(() => _aspect = a),
                                  onCount: (n) => setState(() => _count = n),
                                  expanded: _mediaExpanded,
                                  onToggleExpanded: () => setState(() => _mediaExpanded = !_mediaExpanded),
                                  onRemix: (ref) => _toImageChat(reference: ref),
                                  refresh: _mediaRefresh,
                                )
                              : openItem == null
                              ? rows"""),
    ("""    final activePills = categoryPills;
""", """    final activePills = categoryPills;
    final media = _activeCategory == ModelCategory.image;
"""),
    ("""              child: MarketScreen(
                onClose: () => _requestSwitchSurface(null),
                view: _marketCategory,""", """              child: MarketScreen(
                onClose: () => _requestSwitchSurface(null),
                view: _marketCategory,
                onImagine: (t) => _toImageChat(text: t),
                onRemix: (ref) => _toImageChat(reference: ref),"""),
])
