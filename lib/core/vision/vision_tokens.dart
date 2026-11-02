import 'package:material_ui/material_ui.dart';
import 'package:google_fonts/google_fonts.dart';

/// Collider Vision design tokens.
///
/// Sources:
///  - Type scale, radii, spacing, blur, shadows, text/border/overlay colours and
///    accents: `visionOS copilot kit.tsx` (DS tokens, dark theme).
///  - Glass materials per depth plane: `lib/core/theme/spatial_theme.dart`.
///  - Cell / active fills: the shipping Collider widgets (0x14 rest, 0x38 active).
class VColors {
  VColors._();

  // Text (kit dark theme)
  static const Color textPrimary = Color(0xFFFFFFFF);
  static const Color textSecondary = Color(0xB3FFFFFF); // rgba(255,255,255,0.70)
  static const Color textTertiary = Color(0x73FFFFFF); // rgba(255,255,255,0.45)

  // Borders (kit dark theme)
  static const Color borderSubtle = Color(0x18FFFFFF); // 0.09
  static const Color borderLight = Color(0x1FFFFFFF); // 0.12
  static const Color borderHeavy = Color(0x3DFFFFFF); // 0.24

  // Overlays (kit)
  static const Color overlayLight = Color(0x2EFFFFFF); // 0.18
  static const Color overlayDark = Color(0x59000000); // 0.35

  // Kit glass (opaque-leaning fallback surfaces)
  static const Color glassDark = Color(0xBF14141E); // rgba(20,20,30,0.75)
  static const Color glassDarkHeavy = Color(0x8C14141E); // rgba(20,20,30,0.55)

  // Materials per depth plane (spatial_theme.dart)
  // Copied from the Figma Reference Map nodes (see _ds_work/patch_map_kit_1003.py for the sources).
  //
  // Apple's glass is a light translucent layer: it lets the colour of what is behind it through
  // and adapts to it (HIG, Materials: "glass automatically adapts to the luminance of the objects
  // and colors behind it"). A mid grey at the same density does the opposite, it cancels the hue
  // and turns every pane into the same neutral card, which is what made the app drab. These are
  // a cool white at the same density, so the wallpaper's colour survives the glass.
  // See docs/VISIONOS_DESIGN_SYSTEM.md.
  static const Color glassPrompt = Color(0x1AFFFFFF); // pane: #FFFFFF 10%
  static const Color glassResting = Color(0x1AFFFFFF); // pane: #FFFFFF 10%
  static const Color glassElevated = Color(0x2EF2F5F9); // bars and ornaments: a cool white 18% (was 30%; Claude, 2026-10-23)
  static const Color glassModal = Color(0x2EF2F5F9); // alerts and menus: a cool white 18% (was 30%; Claude, 2026-10-23)
  static const Color glassWork = Color(0x24F2F5F9); // windows: a cool white 14%, the content layer (was 22%; Claude, 2026-10-23)

  // Apple's thickness scale, used for the job Apple gives each one.
  static const Color glassThin = Color(0x26FFFFFF); // thin: brings attention to a control or a selected item
  static const Color glassThick = Color(0x8C0E1118); // thick: a dark element that stays distinct on a regular background
  static const Color glassUltraThin = Color(0x14FFFFFF); // ultraThin: a full screen view that wants a light scheme

  // Cell fills (shipping widgets)
  static const Color fillCell = Color(0x1FFFFFFF); // round controls: #FFFFFF 12%
  static const Color fillActive = Color(0x4DFFFFFF); // controls on a bar, selected: #FFFFFF 30%
  static const Color fillRecessed = Color(0x4D000000); // recessed fields: #000000 30%
  static const Color fillRow = Color(0x29000000); // rows in a pane: #000000 16%

  // Accents (kit)
  static const Color accentBlue = Color(0xFF0A84FF);
  static const Color accentGreen = Color(0xFF30D158);
  static const Color accentRed = Color(0xFFFF453A);
  static const Color accentOrange = Color(0xFFFF9F0A);
  static const Color accentPurple = Color(0xFFBF5AF2);
  static const Color accentTeal = Color(0xFF64D2FF);
}

class VRadius {
  VRadius._();
  static const double xs = 6;
  static const double sm = 10;
  static const double md = 14;
  static const double lg = 22;
  static const double xl = 32;
  static const double card = 32; // pane 417:6826: 40 at the pane's own width
  static const double row = 13; // row 417:6826: 16
  static const double sheet = 32;
  static const double full = 999;
}

class VSpace {
  VSpace._();
  static const double xxs = 4;
  static const double xs = 8;
  static const double sm = 12;
  static const double md = 16;
  static const double lg = 20;
  static const double xl = 24;
  static const double xxl = 32;
  static const double xxxl = 40;
}

class VBlur {
  VBlur._();
  static const double light = 12;
  static const double medium = 20;
  static const double heavy = 32;
  static const double sheet = 40;
}

class VShadow {
  VShadow._();
  static const List<BoxShadow> subtle = [
    BoxShadow(color: Color(0x14000000), blurRadius: 12, offset: Offset(0, 4)),
  ];
  static const List<BoxShadow> medium = [
    BoxShadow(color: Color(0x1F000000), blurRadius: 24, offset: Offset(0, 8)),
  ];
  static const List<BoxShadow> heavy = [
    BoxShadow(color: Color(0x2E000000), blurRadius: 48, offset: Offset(0, 16)),
  ];
  /// Pane 417:6826: 0/40/30 black 5%.
  static const List<BoxShadow> pane = [
    BoxShadow(color: Color(0x0D000000), blurRadius: 30, offset: Offset(0, 40)),
  ];

  /// Ornaments 417:15864: 0/8/6 black 5%.
  static const List<BoxShadow> ornament = [
    BoxShadow(color: Color(0x0D000000), blurRadius: 6, offset: Offset(0, 8)),
  ];
  static const List<BoxShadow> recessed = [
    BoxShadow(color: Color(0x59000000), blurRadius: 18, offset: Offset(0, 10)),
  ];
}

/// Kit type scale. Instrument Sans stands in for SF Pro Text.
class VType {
  VType._();
  static const double xs = 11;
  static const double sm = 11; // 13 until 2026-10-23 (Claude): 11 is the size outside headers
  static const double md = 11; // 15 until 2026-10-23 (Claude): 11 is the size outside headers
  static const double lg = 17;
  static const double xl = 20;
  static const double xxl = 24;
  static const double displaySm = 28;
  static const double displayMd = 34;
  static const double displayLg = 40;

  static const double tight = 1.1;
  static const double normal = 1.3;
  static const double relaxed = 1.45;

  static TextStyle _t(double size, FontWeight w, Color c, double h) =>
      GoogleFonts.instrumentSans(fontSize: size, fontWeight: w, color: c, height: h, letterSpacing: -0.1);

  static TextStyle display({Color color = VColors.textPrimary}) => _t(displaySm, FontWeight.w700, color, tight);
  static TextStyle title({Color color = VColors.textPrimary}) => _t(xxl, FontWeight.w700, color, tight);
  static TextStyle title2({Color color = VColors.textPrimary}) => _t(xl, FontWeight.w700, color, normal);
  static TextStyle headline({Color color = VColors.textPrimary}) => _t(lg, FontWeight.w600, color, normal);
  static TextStyle body({Color color = VColors.textPrimary, FontWeight weight = FontWeight.w400}) => _t(md, weight, color, relaxed);
  static TextStyle callout({Color color = VColors.textPrimary, FontWeight weight = FontWeight.w500}) => _t(sm, weight, color, normal);
  static TextStyle footnote({Color color = VColors.textSecondary, FontWeight weight = FontWeight.w400}) => _t(sm, weight, color, normal);
  static TextStyle caption({Color color = VColors.textTertiary, FontWeight weight = FontWeight.w400}) => _t(xs, weight, color, normal);
}

/// Overlay law: an overlay is a pause menu — small, temporary, content-hugging.
/// The wallpaper and the resting content stay visible and sharp around it;
/// the dim is light and never blurred. Nothing an overlay shows is full width.
class VOverlay {
  VOverlay._();

  /// Light, unblurred dim behind any overlay.
  static const Color scrim = Color(0x33000000); // black 20%

  static bool _phone(BuildContext c) => MediaQuery.sizeOf(c).width < 768;

  /// Menus: settings, history, models, skills, tiers, zoom, alert.
  static double menuWidth(BuildContext c) {
    final w = MediaQuery.sizeOf(c).width;
    return _phone(c) ? (w - 104).clamp(240.0, 300.0) : 340.0;
  }

  static double menuMaxHeight(BuildContext c) => MediaQuery.sizeOf(c).height * 0.46;

  /// Tools: Smart Gen, Discover, Files, Browser, Consensus.
  static double toolWidth(BuildContext c) {
    final w = MediaQuery.sizeOf(c).width;
    return _phone(c) ? (w - 104).clamp(260.0, 300.0) : (w * 0.46).clamp(480.0, 640.0);
  }

  static double toolMaxHeight(BuildContext c) => MediaQuery.sizeOf(c).height * (_phone(c) ? 0.56 : 0.6);
}

class VMotion {
  VMotion._();
  static const double pressedScale = 0.97;
  static const double pressedOpacity = 0.9;
  static const Duration fast = Duration(milliseconds: 140);
  static const Duration base = Duration(milliseconds: 240);
}
