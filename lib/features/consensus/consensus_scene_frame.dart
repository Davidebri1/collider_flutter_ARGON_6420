// Platform switch for the consensus scene host (source: ConsensusScene.tsx).
// On web the scene is an <iframe srcdoc> fed by postMessage, exactly as in the
// source app. Elsewhere this stub is never built (the webview path is used).
export 'consensus_scene_frame_stub.dart'
    if (dart.library.js_interop) 'consensus_scene_frame_web.dart';
