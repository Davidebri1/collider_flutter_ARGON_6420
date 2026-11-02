# Made by Claude (2026-10-20). One-time edit: the music bar pauses while Voice Chat is on (the microphone would
# otherwise hear the song, and Apple: "lower the volume of the soundscape or stop it completely" when other audio
# plays), and plays on when Voice Chat is turned off.
import os
root = os.path.join(os.path.dirname(__file__), "..")
p = os.path.join(root, "lib", "main.dart")
s = open(p, encoding="utf-8").read()
a = ("    setState(() {\n      _voiceChat = on;\n      _voicePhase = '';\n    });\n    if (on) {\n      _voiceTurn();\n    } else {\n"
     "      Voice.instance.cancelListening();\n      Voice.instance.stopSpeaking();\n    }\n")
b = ("    setState(() {\n      _voiceChat = on;\n      _voicePhase = '';\n    });\n    final music = MusicPlayer.instance;\n    if (on) {\n"
     "      _musicHeldForVoice = music.playing;\n      if (music.playing) music.toggle();\n      _voiceTurn();\n    } else {\n"
     "      Voice.instance.cancelListening();\n      Voice.instance.stopSpeaking();\n"
     "      if (_musicHeldForVoice && !music.playing) music.toggle();\n      _musicHeldForVoice = false;\n    }\n")
assert s.count(a) == 1, "voice block"
s = s.replace(a, b)
a2 = "  String _voicePhase = ''; // listening, thinking, speaking, or '' waiting for a tap\n"
assert s.count(a2) == 1
s = s.replace(a2, a2 + "  bool _musicHeldForVoice = false; // the music bar was playing when Voice Chat came on\n")
if "core/audio/music_player.dart" not in s:
    s = s.replace("import 'core/voice/voice.dart';\n", "import 'core/voice/voice.dart';\nimport 'core/audio/music_player.dart';\n", 1)
open(p, "w", encoding="utf-8", newline="").write(s)
print("ok")
