// Audio engine placeholder for platforms without the web player. Made by Claude.
class AudioEngine {
  void Function()? onEnded;
  void Function()? onBlocked;
  void Function(double position, double duration)? onTime;
  void play(String url) {}
  void pause() {}
  void setMuted(bool m) {}
  void seek(double seconds) {}
  void stop() {}
}
