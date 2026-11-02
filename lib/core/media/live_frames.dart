// A live wallpaper's video as pictures the app draws itself. Made by Claude (2026-10-17), after the frame copying in
// Grok's live_cover_video_web.dart. On the web a muted, looping <video> plays outside the app and its frames are copied
// into the app's canvas at the size asked for, so a cover keeps its tilt, clip and reflection (one frame feeds both),
// and the market's background is blurred from a small copy instead of a full-screen one. Elsewhere it gives no frames
// and the poster stays.
export 'live_frames_stub.dart' if (dart.library.js_interop) 'live_frames_web.dart';
