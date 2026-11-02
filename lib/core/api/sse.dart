// Server-sent events from the local server. Made by Claude (2026-10-19).
// The browser's own EventSource on the web; elsewhere there is none, and the caller polls instead.
export 'sse_stub.dart' if (dart.library.js_interop) 'sse_web.dart';
