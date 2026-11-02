// Made by Claude (2026-10-20). Outside a browser there is no microphone or speech here.
import 'package:flutter/foundation.dart';

class Voice {
  Voice._();
  static final Voice instance = Voice._();
  final ValueNotifier<double> level = ValueNotifier(0);
  bool get supported => false;
  Future<String?> listen() async => null;
  void finishListening() {}
  void cancelListening() {}
  Future<void> speak(String text) async {}
  void stopSpeaking() {}
}
