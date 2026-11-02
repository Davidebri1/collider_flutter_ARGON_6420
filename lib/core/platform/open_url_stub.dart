// Made by Claude.
// The phone and desktop apps (Claude, 2026-10-23: openUrl did nothing outside the browser; it now hands the address to
// the system, which opens the app that takes it).
import 'package:url_launcher/url_launcher.dart';

void openUrl(String url) {
  final u = Uri.tryParse(url);
  if (u != null) launchUrl(u, mode: LaunchMode.externalApplication);
}

Future<bool> shareText(String text) async => false;

bool get canShareText => false;

bool get onThisComputer => false;

Future<bool> shareFile(List<int> bytes, String name, String mime) async => false;
