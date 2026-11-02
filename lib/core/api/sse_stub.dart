// Made by Claude (2026-10-19). No EventSource off the web: the caller falls back to polling.
Stream<String> sseEvents(String url) => Stream.error(UnsupportedError('server-sent events'));
