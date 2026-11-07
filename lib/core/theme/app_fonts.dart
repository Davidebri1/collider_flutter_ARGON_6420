import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'dart:ui' as ui show FontFeature, Shadow;

/// Shared typography bridge for Instrument Sans, Cormorant Garamond, and Inter.
class AppFonts {
  AppFonts._();

  static TextStyle instrumentSans({
    bool inherit = true,
    Color? color,
    Color? backgroundColor,
    double? fontSize,
    FontWeight? fontWeight,
    FontStyle? fontStyle,
    double? letterSpacing,
    double? wordSpacing,
    TextBaseline? textBaseline,
    double? height,
    ui.Shadow? shadow,
    List<ui.Shadow>? shadows,
    List<ui.FontFeature>? fontFeatures,
    TextDecoration? decoration,
    Color? decorationColor,
    TextDecorationStyle? decorationStyle,
    double? decorationThickness,
    List<String>? fontFamilyFallback,
    String? debugLabel,
    Locale? locale,
  }) {
    return GoogleFonts.instrumentSans(
      color: color,
      backgroundColor: backgroundColor,
      fontSize: fontSize,
      fontWeight: fontWeight,
      fontStyle: fontStyle,
      letterSpacing: letterSpacing,
      wordSpacing: wordSpacing,
      textBaseline: textBaseline,
      height: height,
      shadows: shadows ?? (shadow == null ? null : [shadow]),
      fontFeatures: fontFeatures,
      decoration: decoration,
      decorationColor: decorationColor,
      decorationStyle: decorationStyle,
      decorationThickness: decorationThickness,
      locale: locale,
    ).copyWith(
      inherit: inherit,
      fontFamilyFallback: fontFamilyFallback,
      debugLabel: debugLabel,
    );
  }

  static TextStyle cormorantGaramond({
    bool inherit = true,
    Color? color,
    Color? backgroundColor,
    double? fontSize,
    FontWeight? fontWeight,
    FontStyle? fontStyle,
    double? letterSpacing,
    double? wordSpacing,
    TextBaseline? textBaseline,
    double? height,
    ui.Shadow? shadow,
    List<ui.Shadow>? shadows,
    List<ui.FontFeature>? fontFeatures,
    TextDecoration? decoration,
    Color? decorationColor,
    TextDecorationStyle? decorationStyle,
    double? decorationThickness,
    List<String>? fontFamilyFallback,
    String? debugLabel,
    Locale? locale,
  }) {
    return GoogleFonts.cormorantGaramond(
      color: color,
      backgroundColor: backgroundColor,
      fontSize: fontSize,
      fontWeight: fontWeight,
      fontStyle: fontStyle,
      letterSpacing: letterSpacing,
      wordSpacing: wordSpacing,
      textBaseline: textBaseline,
      height: height,
      shadows: shadows ?? (shadow == null ? null : [shadow]),
      fontFeatures: fontFeatures,
      decoration: decoration,
      decorationColor: decorationColor,
      decorationStyle: decorationStyle,
      decorationThickness: decorationThickness,
      locale: locale,
    ).copyWith(
      inherit: inherit,
      fontFamilyFallback: fontFamilyFallback,
      debugLabel: debugLabel,
    );
  }

  static TextStyle inter({
    bool inherit = true,
    Color? color,
    Color? backgroundColor,
    double? fontSize,
    FontWeight? fontWeight,
    FontStyle? fontStyle,
    double? letterSpacing,
    double? wordSpacing,
    TextBaseline? textBaseline,
    double? height,
    ui.Shadow? shadow,
    List<ui.Shadow>? shadows,
    List<ui.FontFeature>? fontFeatures,
    TextDecoration? decoration,
    Color? decorationColor,
    TextDecorationStyle? decorationStyle,
    double? decorationThickness,
    List<String>? fontFamilyFallback,
    String? debugLabel,
    Locale? locale,
  }) {
    return GoogleFonts.inter(
      color: color,
      backgroundColor: backgroundColor,
      fontSize: fontSize,
      fontWeight: fontWeight,
      fontStyle: fontStyle,
      letterSpacing: letterSpacing,
      wordSpacing: wordSpacing,
      textBaseline: textBaseline,
      height: height,
      shadows: shadows ?? (shadow == null ? null : [shadow]),
      fontFeatures: fontFeatures,
      decoration: decoration,
      decorationColor: decorationColor,
      decorationStyle: decorationStyle,
      decorationThickness: decorationThickness,
      locale: locale,
    ).copyWith(
      inherit: inherit,
      fontFamilyFallback: fontFamilyFallback,
      debugLabel: debugLabel,
    );
  }

  static TextTheme instrumentSansTextTheme([TextTheme? base]) {
    return GoogleFonts.instrumentSansTextTheme(base ?? ThemeData.dark().textTheme);
  }
}
