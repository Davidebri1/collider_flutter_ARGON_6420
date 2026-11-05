import 'package:material_ui/material_ui.dart';
import 'package:google_fonts/google_fonts.dart';

/// Collider Vision design tokens (Unified VisionOS Optical Glass, Light Emittance & Crisp Body Hierarchy).
class VColors {
  VColors._();

  // Text (visionOS high-contrast optical legibility)
  static const Color textPrimary = Color(0xFFFFFFFF);
  static const Color textSecondary = Color(0xF0FFFFFF); // rgba(255,255,255,0.94)
  static const Color textTertiary = Color(0xC2FFFFFF); // rgba(255,255,255,0.76)

  // Borders (specular optical rims)
  static const Color borderSubtle = Color(0x2EFFFFFF); // 0.18
  static const Color borderLight = Color(0x42FFFFFF); // 0.26
  static const Color borderHeavy = Color(0x66FFFFFF); // 0.40

  // Overlays
  static const Color overlayLight = Color(0x26FFFFFF); // 0.15
  static const Color overlayDark = Color(0x66000000); // 0.40

  // Kit fallback surfaces
  static const Color glassDark = Color(0xD90E121C);
  static const Color glassDarkHeavy = Color(0xE60B0F17);

  // Unified VisionOS Optical Glass Materials (Shared across Side Nav, Bottom Dock, Composer, and Ticker)
  // Dark translucent optical glass for high contrast and crisp lettering/icon visibility over any living wallpaper.
  static const Color glassPrompt = Color(0x8C0E121C); // Plane 2: Floating Composer (55% dark translucent glass)
  static const Color glassResting = Color(0x940E121C); // Plane 1: Resting Ticker Window (58% dark translucent glass)
  static const Color glassElevated = Color(0xA6101520); // Plane 3: Unified Ornaments (Side Nav Rail & Bottom Dock, 65% dark glass)
  static const Color glassModal = Color(0xD90E121C); // Plane 4: Floating Menus & Modals (85% dark glass)
  static const Color glassWork = Color(0xA60E121C); // Plane 3: Durable Work Windows (Smart Gen, Discover, Files, 65% dark glass)

  // Apple thickness scale
  static const Color glassThin = Color(0x730E121C);
  static const Color glassThick = Color(0xB8101520);
  static const Color glassUltraThin = Color(0x590E121C);

  // Inner cell fills (no nested blur; balanced luminance contrast)
  static const Color fillCell = Color(0x18FFFFFF); // 9.5% white
  static const Color fillActive = Color(0x26FFFFFF); // 15% white active capsule (toned down from glaring 0x38FFFFFF)
  static const Color fillRecessed = Color(0x47000000); // 28% black recessed well
  static const Color fillRow = Color(0x38000000);

  // Emissive Accents (Light Emittance palette)
  static const Color accentBlue = Color(0xFF0A84FF);
  static const Color accentGreen = Color(0xFF30D158);
  static const Color accentRed = Color(0xFFFF453A);
  static const Color accentOrange = Color(0xFFFF9F0A);
  static const Color accentGold = Color(0xFFFFD60A);
  static const Color accentPurple = Color(0xFFBF5AF2);
  static const Color accentTeal = Color(0xFF64D2FF);
  static const Color accentCyan = Color(0xFF38BDF8);
}

class VRadius {
  VRadius._();
  static const double xs = 8;
  static const double sm = 12;
  static const double md = 16;
  static const double lg = 22;
  static const double xl = 26;
  static const double card = 26; // Concentric window radius: 26 - 10 (padding) = 16 (row radius)
  static const double row = 16;
  static const double sheet = 26;
  static const double full = 999;
}

class VSpace {
  VSpace._();
  static const double xxs = 4;
  static const double xs = 8;
  static const double sm = 10;
  static const double md = 14;
  static const double lg = 18;
  static const double xl = 22;
  static const double xxl = 28;
  static const double xxxl = 36;
}

class VBlur {
  VBlur._();
  static const double light = 14;
  static const double medium = 22;
  static const double heavy = 32;
  static const double sheet = 40;
}

class VShadow {
  VShadow._();
  static const List<BoxShadow> subtle = [
    BoxShadow(color: Color(0x24000000), blurRadius: 14, offset: Offset(0, 6)),
  ];
  static const List<BoxShadow> medium = [
    BoxShadow(color: Color(0x33000000), blurRadius: 24, offset: Offset(0, 10)),
  ];
  static const List<BoxShadow> heavy = [
    BoxShadow(color: Color(0x47000000), blurRadius: 44, offset: Offset(0, 18)),
  ];

  /// Unified elevation shadow for primary glass windows (Ticker, Smart Gen, Discover, Files).
  static const List<BoxShadow> pane = [
    BoxShadow(color: Color(0x42000000), blurRadius: 32, offset: Offset(0, 16)),
    BoxShadow(color: Color(0x14FFFFFF), blurRadius: 1, offset: Offset(0, -0.5)),
  ];

  /// Unified elevation shadow for floating ornaments (Side Nav Rail, Bottom Dock, Floating Composer).
  static const List<BoxShadow> ornament = [
    BoxShadow(color: Color(0x4D000000), blurRadius: 24, offset: Offset(0, 12)),
    BoxShadow(color: Color(0x1AFFFFFF), blurRadius: 1, offset: Offset(0, -0.5)),
  ];

  static const List<BoxShadow> recessed = [
    BoxShadow(color: Color(0x59000000), blurRadius: 18, offset: Offset(0, 10)),
  ];

  /// Live Light Emittance helper: projects radial colored light bloom outside active controls/badges onto surrounding glass.
  static List<BoxShadow> emissive(Color hue, {double intensity = 0.55, double radius = 14}) => [
        BoxShadow(
          color: hue.withValues(alpha: (intensity * 0.72).clamp(0.0, 1.0)),
          blurRadius: radius,
          spreadRadius: 0.0,
          blurStyle: BlurStyle.outer,
        ),
        BoxShadow(
          color: hue.withValues(alpha: (intensity * 0.32).clamp(0.0, 1.0)),
          blurRadius: radius * 1.6,
          spreadRadius: 0.0,
          blurStyle: BlurStyle.outer,
        ),
      ];
}

class VType {
  VType._();
  static const double xxs = 10.5; // Hierarchy 7: Spatial Ornament / Micro Caption (10.5pt)
  static const double xs = 11.0; // Hierarchy 6: Metadata Caption (11.0pt)
  static const double sm = 11.5; // Hierarchy 5: Message Body & Summary (11.5pt)
  static const double md = 11.5; // Hierarchy 5: Message Body & Summary (11.5pt)
  static const double rowHdr = 12.5; // Hierarchy 4: Model Name / Card Header (12.5pt)
  static const double lg = 15.5; // Hierarchy 3: Section Header
  static const double xl = 17.5; // Hierarchy 3+: Sub-window Title
  static const double xxl = 19.5; // Hierarchy 2: Window Title
  static const double displaySm = 24.0; // Hierarchy 1: Display
  static const double displayMd = 30.0;
  static const double displayLg = 36.0;

  static const double tight = 1.15;
  static const double normal = 1.28;
  static const double relaxed = 1.40;

  static TextStyle _t(double size, FontWeight w, Color c, double h, {double spacing = -0.1}) =>
      GoogleFonts.instrumentSans(fontSize: size, fontWeight: w, color: c, height: h, letterSpacing: spacing);

  /// Hierarchy 1: Hero Display
  static TextStyle display({Color color = VColors.textPrimary}) => _t(displaySm, FontWeight.w700, color, tight, spacing: -0.3);

  /// Hierarchy 2: Primary Window Title
  static TextStyle title({Color color = VColors.textPrimary}) => _t(xxl, FontWeight.w700, color, tight, spacing: -0.2);

  /// Hierarchy 3: Section Header
  static TextStyle title2({Color color = VColors.textPrimary}) => _t(lg, FontWeight.w600, color, normal, spacing: -0.15);

  /// Hierarchy 4: Row / Model / Card Header
  static TextStyle headline({Color color = VColors.textPrimary, FontWeight weight = FontWeight.w600}) =>
      _t(rowHdr, weight, color, normal, spacing: -0.1);

  /// Hierarchy 5: Crisp Message Body & 2-Line Summary
  static TextStyle body({Color color = VColors.textPrimary, FontWeight weight = FontWeight.w500}) =>
      _t(md, weight, color, relaxed, spacing: 0.0);

  /// Hierarchy 5 (Alias): Standardized Summary (up to 2 lines)
  static TextStyle summary({Color color = VColors.textSecondary, FontWeight weight = FontWeight.w500}) =>
      _t(md, weight, color, normal, spacing: 0.0);

  /// Hierarchy 5: Interactive Control / Callout
  static TextStyle callout({Color color = VColors.textPrimary, FontWeight weight = FontWeight.w600}) =>
      _t(sm, weight, color, normal, spacing: -0.05);

  /// Hierarchy 5: Secondary Body / Footnote
  static TextStyle footnote({Color color = VColors.textSecondary, FontWeight weight = FontWeight.w500}) =>
      _t(sm, weight, color, normal, spacing: 0.0);

  /// Hierarchy 6: Metadata / Timestamp / Badge
  static TextStyle caption({Color color = VColors.textTertiary, FontWeight weight = FontWeight.w600}) =>
      _t(xs, weight, color, normal, spacing: 0.06);

  /// Hierarchy 7: Spatial Ornament / Tabular Micro-Caption
  static TextStyle metaCaption({Color color = VColors.textTertiary, FontWeight weight = FontWeight.w600}) =>
      _t(xxs, weight, color, tight, spacing: 0.08);
}

/// Overlay sizing law for 9:16 mobile portrait and desktop viewports.
class VOverlay {
  VOverlay._();

  static const Color scrim = Color(0x38000000);

  static bool _phone(BuildContext c) => MediaQuery.sizeOf(c).width < 768;

  /// Menus: settings, history, models, skills, tiers, zoom, alert (Snap Popovers <= 1/4 screen height).
  static double menuWidth(BuildContext c) {
    final w = MediaQuery.sizeOf(c).width;
    return _phone(c) ? (w * 0.60).clamp(220.0, 246.0) : 268.0;
  }

  static double menuMaxHeight(BuildContext c) => (MediaQuery.sizeOf(c).height * 0.25).clamp(184.0, 224.0);

  /// Tools: Smart Gen, Discover, Files, Browser, Consensus.
  static double toolWidth(BuildContext c) {
    final w = MediaQuery.sizeOf(c).width;
    return _phone(c) ? (w - 64).clamp(276.0, 336.0) : (w * 0.52).clamp(480.0, 680.0);
  }

  static double toolMaxHeight(BuildContext c) => MediaQuery.sizeOf(c).height * (_phone(c) ? 0.62 : 0.66);
}

class VMotion {
  VMotion._();
  static const double pressedScale = 0.96;
  static const double pressedOpacity = 0.9;
  static const Duration fast = Duration(milliseconds: 140);
  static const Duration base = Duration(milliseconds: 240);
}
