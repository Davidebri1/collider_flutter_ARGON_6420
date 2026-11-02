import 'dart:convert';
import 'dart:math' as math;

import 'package:material_ui/material_ui.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:webview_flutter/webview_flutter.dart';
import 'package:flutter/services.dart' show rootBundle;
import '../../core/vision/vision_kit.dart';
import 'consensus_scene_frame.dart';
import 'consensus_view.dart';
import '../../core/api/collider_api.dart' as api;
import '../../models/model_def.dart';

/// Consensus Topology screen.
///
/// Drop-in of the consensus scene from collidermergedx3-glm
/// (src/components/ConsensusScene.tsx + consensus-scene-template.ts +
/// src/services/consensusView.ts, payload built as in ConsensusDrawer.tsx).
/// The scene is a self-contained HTML/CSS 2.5D map; it has no mesh or model
/// assets. On web it is hosted in an iframe fed by postMessage, as in the
/// source; on native it runs in a WebView fed by runJavaScript.
///
/// The scene sits in a window on every screen size and keeps its own header
/// (back / CONSENSUS / LABELS). Under each sphere is the model's name, written out.
class ConsensusWebView extends StatefulWidget {
  final VoidCallback? onClose;
  final Function(String modelId)? onModelSelected;
  final api.JobState? job;

  const ConsensusWebView({
    super.key,
    this.onClose,
    this.onModelSelected,
    this.job,
  });

  static String? _cachedHtml;
  static Future<String?> preload() async {
    if (_cachedHtml != null) return _cachedHtml;
    try {
      _cachedHtml = await rootBundle.loadString('assets/html/consensus.html');
    } catch (_) {}
    return _cachedHtml;
  }

  @override
  State<ConsensusWebView> createState() => _ConsensusWebViewState();
}

class _DemoModel {
  final String id, label, short, color, view;
  final String? reply;
  const _DemoModel(this.id, this.label, this.short, this.color, this.view, [this.reply]);
}

// No made-up run (Claude, 2026-10-17, after Grok's build): with nothing asked yet the map is empty.

class _ConsensusWebViewState extends State<ConsensusWebView> {
  static String _hex(Color c) => '#${(c.toARGB32() & 0xFFFFFF).toRadixString(16).padLeft(6, '0')}';
  static final Map<String, String> _payloadMemo = {};

  /// Models of the live session; none before anything has been asked.
  List<_DemoModel> get _models {
    final j = widget.job;
    if (j == null) return const [];
    return [
      for (final e in j.results.entries)
        if (e.value.status == 'done' && ModelRoster.byId(e.key) != null)
          _DemoModel(e.key, ModelRoster.byId(e.key)!.label, ModelRoster.byId(e.key)!.label,
              _hex(ModelRoster.byId(e.key)!.providerColor), e.value.essence),
    ];
  }

  ConsensusResult get _result {
    final j = widget.job;
    if (j == null) return const ConsensusResult(claims: [], groups: []);
    final done = j.results.entries.where((e) => e.value.status == 'done').toList();
    return ConsensusResult(
      claims: [
        for (final e in done) ConsensusClaim(modelId: e.key, essence: e.value.essence, chains: j.consensus.chains[e.key] ?? 3),
      ],
      groups: j.consensus.groups.isNotEmpty ? j.consensus.groups : [for (final e in done) [e.key]],
      need: j.consensus.need,
      tieBreakBecause: j.consensus.tieBasis.isEmpty ? null : j.consensus.tieBasis,
    );
  }

  WebViewController? _controller;
  bool _isLoading = true;
  String? _html;
  // Live essences are full sentences; labels open on demand so the spheres stay readable.
  bool _labels = false;
  String _tab = 'total';
  String _lastPayload = '{}';

  @override
  void initState() {
    super.initState();
    if (ConsensusWebView._cachedHtml != null) {
      _html = ConsensusWebView._cachedHtml;
      if (kIsWeb) _isLoading = false;
      if (!kIsWeb) _initNative(_html!);
    } else {
      ConsensusWebView.preload().then((html) {
        if (!mounted || html == null) {
          if (mounted) setState(() => _isLoading = false);
          return;
        }
        setState(() {
          _html = html;
          if (kIsWeb) _isLoading = false;
        });
        if (!kIsWeb) _initNative(html);
      });
    }
  }

  void _initNative(String html) {
    try {
      final ctrl = WebViewController();
      try {
        ctrl.setJavaScriptMode(JavaScriptMode.unrestricted);
        ctrl.setBackgroundColor(const Color(0xFF07080B));
      } catch (_) {}
      try {
        ctrl.addJavaScriptChannel(
          'FlutterBridge',
          onMessageReceived: (JavaScriptMessage message) {
            if (message.message.contains('CLOSE')) {
              widget.onClose?.call();
            } else if (message.message.startsWith('MODEL:')) {
              final modelId = message.message.split(':')[1];
              widget.onModelSelected?.call(modelId);
            }
          },
        );
      } catch (_) {}
      try {
        ctrl.setNavigationDelegate(
          NavigationDelegate(
            onPageFinished: (String url) {
              if (mounted) {
                setState(() => _isLoading = false);
                _pushNative();
              }
            },
          ),
        );
      } catch (_) {}
      setState(() => _controller = ctrl);
      ctrl.loadHtmlString(html);
    } catch (_) {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _pushNative() {
    try {
      _controller?.runJavaScript('''
        (function(){
          if (window.ColliderConsensus) window.ColliderConsensus.update($_lastPayload);
          var b = document.getElementById('btnBack');
          if (b && !b.__flutterBound && window.FlutterBridge) {
            b.__flutterBound = true;
            b.addEventListener('click', function(){ FlutterBridge.postMessage('CLOSE'); });
          }
        })();
      ''');
    } catch (_) {}
  }

  /// Scene payload, built as ConsensusDrawer.tsx builds `scenePayload`.
  String _buildPayload(double fieldW, double fieldH) {
    final j = widget.job;
    final doneSig = _models.map((m) => '${m.id}:${m.view.hashCode}').join(',');
    final memoKey = '${j?.id ?? "none"}|${j?.consensus.summary.hashCode}|$doneSig|${fieldW.round()}x${fieldH.round()}|$_labels|$_tab';
    final cached = _payloadMemo[memoKey];
    if (cached != null) return cached;

    final derived = deriveConsensus(_result)!;
    final mapScale = math.max(1.0, math.min(2.6, fieldH / 190));
    int scaled(num px) => (px * mapScale).round();
    var nucleusSize = scaled(derived.nucleusSize);
    final nucleusRadius = nucleusSize / 2;
    final centerX = fieldW / 2;
    final centerY = (fieldH * 0.44).roundToDouble();
    final bottomReserve = _labels ? 120.0 : 56.0;
    final innerR = math.max(nucleusRadius + 34, 58.0);
    final outerR = math.max(innerR + 40, math.min(fieldW / 2 - 52, fieldH - bottomReserve - centerY));
    final placements = layoutByMatches(
      derived,
      _result,
      Field(width: fieldW, height: fieldH, centerX: centerX, centerY: centerY, innerR: innerR, outerR: outerR),
    );
    // Fit to the viewport: if any sphere + its label (label box max 120px)
    // would cross the side edges, scale every offset from the nucleus, and the
    // nucleus itself, by one factor. Proportions stay as the source draws them.
    const edgePad = 64.0; // half of the 120px label box + 4px margin
    final maxHalf = fieldW / 2 - edgePad;
    var extent = innerR;
    for (final p in placements) {
      extent = math.max(extent, (p.x - centerX).abs());
    }
    final fit = extent > maxHalf && maxHalf > 0 ? maxHalf / extent : 1.0;
    if (fit < 1.0) nucleusSize = (nucleusSize * fit).round();
    final byId = {
      for (final p in placements)
        p.modelId: Placed(
          modelId: p.modelId,
          x: centerX + (p.x - centerX) * fit,
          y: centerY + (p.y - centerY) * fit,
          unanchored: p.unanchored,
          linksToConsensus: p.linksToConsensus,
          inConsensus: p.inConsensus,
        ),
    };
    final claimById = {for (final c in derived.claims) c.modelId: c};

    // No overlaps: resolve sphere/label collisions in screen space. The scene
    // bands y into 34%..92% of the height and puts the nucleus at 59.5%.
    final ms = <_DemoModel>[];
    final chains = <int>[];
    final agree = <bool>[];
    final meta = <Placed>[];
    final start = <Offset>[];
    for (final m in _models) {
      final p = byId[m.id];
      final c = claimById[m.id];
      if (p == null || c == null) continue;
      ms.add(m);
      chains.add(c.chains);
      agree.add(c.inConsensus);
      meta.add(p);
      start.add(Offset(p.x, fieldH * (0.34 + 0.58 * (p.y / fieldH).clamp(0.0, 1.0))));
    }
    final nuc = Offset(fieldW / 2, fieldH * 0.595);
    const label = 18.0;
    const gap = 8.0;
    // in a window the score, the statement and the tabs take the upper part; the spheres keep below them
    final top = fieldH * 0.47, bottom = fieldH * 0.90;
    var sizeScale = 1.0;
    var pos = List<Offset>.of(start);
    for (var attempt = 0; attempt < 14; attempt++) {
      pos = List<Offset>.of(start);
      final r = [for (final k in chains) (30 + k * 10) * sizeScale / 2 + label / 2];
      final nr = nucleusSize * sizeScale / 2 + label / 2;
      var clear = false;
      for (var it = 0; it < 300 && !clear; it++) {
        clear = true;
        for (var i = 0; i < pos.length; i++) {
          var d = pos[i] - nuc;
          var need = r[i] + nr + gap;
          if (d.distance < need) {
            clear = false;
            final dir = d.distance < 0.01 ? Offset(math.cos(i * 1.7), math.sin(i * 1.7)) : d / d.distance;
            pos[i] = nuc + dir * need;
          }
          for (var j = i + 1; j < pos.length; j++) {
            d = pos[j] - pos[i];
            need = r[i] + r[j] + gap;
            if (d.distance < need) {
              clear = false;
              final dir = d.distance < 0.01 ? Offset(math.cos(j * 2.3), math.sin(j * 2.3)) : d / d.distance;
              final push = (need - d.distance) / 2 + 0.5;
              pos[i] -= dir * push;
              pos[j] += dir * push;
            }
          }
        }
        for (var i = 0; i < pos.length; i++) {
          final ri = r[i];
          pos[i] = Offset(
            pos[i].dx.clamp(ri + 6, math.max(ri + 6, fieldW - ri - 6)).toDouble(),
            pos[i].dy.clamp(top + ri, math.max(top + ri, bottom - ri)).toDouble(),
          );
        }
      }
      if (clear) break;
      sizeScale *= 0.9;
    }

    final models = <Map<String, dynamic>>[];
    for (var i = 0; i < ms.length; i++) {
      final m = ms[i];
      final yPct = (((pos[i].dy / fieldH) - 0.34) / 0.58 * 100).clamp(0.0, 100.0);
      models.add({
        'id': m.id,
        'label': m.label,
        'short': m.short,
        'color': m.color,
        'tier': 'free',
        if (m.reply != null) 'reply': m.reply,
        'view': m.view,
        'agree': agree[i],
        'chainDepth': chains[i],
        'unanchored': meta[i].unanchored,
        'x': (pos[i].dx / fieldW) * 100,
        'y': yPct,
      });
    }

    final encoded = jsonEncode({
      'models': models,
      'ratioN': derived.ratioN,
      'ratioM': derived.ratioM,
      'hasRun': true,
      'summary': derived.summary,
      'nucleusSize': (nucleusSize * sizeScale).round(),
      'sizeScale': sizeScale,
      'glowOpacity': derived.glowOpacity,
      'glowRadius': derived.glowRadius,
      'tieBecause': derived.tieBecause ?? '',
      'labels': _labels,
      'activeTab': _tab,
    });
    if (_payloadMemo.length > 32) _payloadMemo.remove(_payloadMemo.keys.first);
    _payloadMemo[memoKey] = encoded;
    return encoded;
  }

  Widget _scene(BoxConstraints c) {
    final w = c.maxWidth.isFinite && c.maxWidth > 0 ? c.maxWidth : 390.0;
    final h = c.maxHeight.isFinite && c.maxHeight > 0 ? c.maxHeight : 700.0;
    if (_models.isEmpty || deriveConsensus(_result) == null) return const SizedBox.expand();
    final payload = _buildPayload(w, h);
    if (!kIsWeb && payload != _lastPayload) {
      _lastPayload = payload;
      WidgetsBinding.instance.addPostFrameCallback((_) => _pushNative());
    }
    _lastPayload = payload;
    return Stack(
      children: [
        if (kIsWeb && _html != null)
          Positioned.fill(
            child: ConsensusSceneFrame(
              html: _html!,
              payloadJson: payload,
              onClose: widget.onClose,
              onLabelsChange: (v) => setState(() => _labels = v),
              onTabChange: (t) => setState(() => _tab = t),
            ),
          )
        else if (!kIsWeb && _controller != null)
          Positioned.fill(child: WebViewWidget(controller: _controller!))
        else if (!_isLoading)
          Center(child: Text('3D Agreement Cluster Topology', style: VType.headline())),
        if (_isLoading)
          const Center(child: CircularProgressIndicator(color: VColors.textSecondary, strokeWidth: 2)),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    // David, 4 Oct 2026: "should be in a window like everything else". The scene is a window over the
    // room, which goes out of focus behind it; the dock stays where it is. The scene carries its own
    // header and its own way back, so the window adds none.
    final size = MediaQuery.of(context).size;
    final isMobile = size.width < 768;
    final width = isMobile ? size.width - 48 : VOverlay.toolWidth(context);
    final height = isMobile ? math.min(size.height - 56 - 108, 600.0) : VOverlay.toolMaxHeight(context);
    return Stack(
      fit: StackFit.expand,
      children: [
        VScrim(onTap: widget.onClose),
        SafeArea(
          child: Align(
            alignment: Alignment.topCenter,
            child: Padding(
              padding: EdgeInsets.only(top: isMobile ? 44 : 40),
              child: SizedBox(
                width: width,
                height: height,
                child: VGlass(
                  material: VMaterial.work,
                  radius: VRadius.xl,
                  padding: EdgeInsets.zero,
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(VRadius.xl),
                    child: ColoredBox(
                      color: const Color(0xFF07080B),
                      child: LayoutBuilder(builder: (context, c) => _scene(c)),
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
