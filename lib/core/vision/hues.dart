// Made by Claude (2026-10-20). Colour for Collider's icons.
// Apple's system colours, at the values visionOS uses (its dark values, HIG "Color"), and the one colour each thing
// carries wherever its icon appears: the same thing is always the same colour, a colour always means the same thing.
// Icons that name a thing (an app, a place, an action, a kind of file) are drawn in its colour, filled where a filled
// glyph exists, as Apple asks for colour in bold shapes rather than thin lines. Plain controls (close, back, more,
// chevrons, send) stay white on glass, as visionOS draws them.
import 'package:material_ui/material_ui.dart';

abstract final class VHue {
  static const red = Color(0xFFFF4245);
  static const orange = Color(0xFFFF9230);
  static const yellow = Color(0xFFFFD600);
  static const green = Color(0xFF30D158);
  static const mint = Color(0xFF00DAC3);
  static const teal = Color(0xFF00D2E0);
  static const cyan = Color(0xFF3CD3FE);
  static const blue = Color(0xFF0091FF);
  static const indigo = Color(0xFF6D7CFF);
  static const purple = Color(0xFFDB34F2);
  static const pink = Color(0xFFFF375F);
  static const brown = Color(0xFFB78A66);
  static const gray = Color(0xFF8E8E93);

  // The apps, matching their icons in the Apps overlay.
  static const smartGen = indigo;
  static const discover = orange;
  static const themeGallery = green;
  static const premiumMarket = purple;
  static const files = blue;
  static const music = pink;
  static const browser = teal;
  static const documents = yellow;
}

final Map<int, Color> _byGlyph = {
  for (final e in <IconData, Color>{
    // composing, history, models, settings, apps
    Icons.edit_note_rounded: VHue.blue,
    Icons.add_comment_outlined: VHue.blue,
    Icons.add_rounded: VHue.green,
    Icons.history_rounded: VHue.purple,
    Icons.hub_outlined: VHue.indigo,
    Icons.tune_rounded: VHue.gray,
    Icons.apps_rounded: VHue.orange,
    Icons.settings_rounded: VHue.gray,
    // what a message or a conversation can do
    Icons.copy_rounded: VHue.blue,
    Icons.bookmark_border_rounded: VHue.orange,
    Icons.bookmark_rounded: VHue.orange,
    Icons.ios_share_rounded: VHue.blue,
    Icons.search_rounded: VHue.cyan,
    Icons.attach_file_rounded: VHue.teal,
    Icons.language_rounded: VHue.teal,
    Icons.public_rounded: VHue.teal,
    Icons.travel_explore_rounded: VHue.teal,
    Icons.download_rounded: VHue.green,
    Icons.upload_rounded: VHue.blue,
    Icons.favorite_rounded: VHue.pink,
    Icons.favorite_border_rounded: VHue.pink,
    Icons.delete_outline_rounded: VHue.red,
    Icons.delete_rounded: VHue.red,
    Icons.visibility_off_outlined: VHue.indigo,
    Icons.mic_rounded: VHue.red,
    Icons.mic_none_rounded: VHue.red,
    Icons.graphic_eq_rounded: VHue.red,
    Icons.edit_rounded: VHue.yellow,
    Icons.open_in_new_rounded: VHue.blue,
    Icons.auto_awesome_rounded: VHue.orange,
    Icons.replay_10_rounded: VHue.blue,
    Icons.forward_10_rounded: VHue.blue,
    Icons.play_arrow_rounded: VHue.blue,
    Icons.pause_rounded: VHue.blue,
    Icons.volume_up_rounded: VHue.blue,
    Icons.volume_off_rounded: VHue.gray,
    // modes
    Icons.chat_bubble_outline_rounded: VHue.blue,
    Icons.article_outlined: VHue.orange,
    Icons.auto_stories_outlined: VHue.purple,
    // places and kinds of files
    Icons.home_rounded: VHue.blue,
    Icons.folder_rounded: VHue.files,
    Icons.folder_open_rounded: VHue.files,
    Icons.article_rounded: VHue.orange,
    Icons.shopping_bag_rounded: VHue.purple,
    Icons.insert_drive_file_rounded: VHue.gray,
    Icons.image_rounded: VHue.yellow,
    Icons.music_note_rounded: VHue.music,
    Icons.videocam_rounded: VHue.purple,
    Icons.picture_as_pdf_rounded: VHue.red,
    Icons.description_rounded: VHue.blue,
    Icons.description_outlined: VHue.blue,
    Icons.view_kanban_outlined: VHue.smartGen,
    Icons.explore_outlined: VHue.discover,
    Icons.collections_rounded: VHue.themeGallery,
    Icons.workspace_premium_rounded: VHue.premiumMarket,
    Icons.terminal_rounded: VHue.gray,
  }.entries)
    e.key.codePoint: e.value,
};

/// The colour of the thing [icon] names, or null for a plain control.
Color? vHueFor(IconData icon) => _byGlyph[icon.codePoint];
