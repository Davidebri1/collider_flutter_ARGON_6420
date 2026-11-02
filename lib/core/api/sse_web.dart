// Made by Claude (2026-10-19). Each message's data, until the server sends "end"; an error ends the stream with an error.
import 'dart:async';
import 'dart:js_interop';

import 'package:web/web.dart' as web;

Stream<String> sseEvents(String url) {
  web.EventSource? es;
  final c = StreamController<String>();
  void finish([Object? error]) {
    es?.close();
    es = null;
    if (c.isClosed) return;
    if (error != null) c.addError(error);
    c.close();
  }

  c.onListen = () {
    final s = es = web.EventSource(url);
    s.onmessage = ((web.MessageEvent e) {
      if (!c.isClosed) c.add('${e.data.dartify()}');
    }).toJS;
    s.addEventListener('end', ((web.Event _) => finish()).toJS);
    s.addEventListener('gone', ((web.Event _) => finish(StateError('not found'))).toJS);
    s.onerror = ((web.Event _) => finish(StateError('stream closed'))).toJS;
  };
  c.onCancel = () => finish();
  return c.stream;
}
