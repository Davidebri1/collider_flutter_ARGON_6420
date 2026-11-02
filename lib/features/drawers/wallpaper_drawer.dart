import '../../core/drafts.dart';
import 'dart:ui';
import 'package:material_ui/material_ui.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../models/theme_def.dart';
import '../../core/theme/vision_pressable.dart';
import '../../core/theme/spatial_theme.dart';

class WallpaperDrawer extends StatefulWidget {
  final WallpaperTheme currentTheme;
  final Function(WallpaperTheme theme) onSelectTheme;
  final VoidCallback onClose;

  const WallpaperDrawer({
    super.key,
    required this.currentTheme,
    required this.onSelectTheme,
    required this.onClose,
  });

  @override
  State<WallpaperDrawer> createState() => _WallpaperDrawerState();
}

class _WallpaperDrawerState extends State<WallpaperDrawer> {
  final TextEditingController _searchCtrl = Drafts.text('wallpaper.search');
  String _searchQuery = '';

  @override
  void dispose() {
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final filteredThemes = WallpaperCatalog.freeThemes.where((t) {
      if (_searchQuery.isEmpty) return true;
      final q = _searchQuery.toLowerCase();
      return t.name.toLowerCase().contains(q) || t.id.toLowerCase().contains(q);
    }).toList();

    return Stack(
      fit: StackFit.expand,
      children: [
        // Clickaway Dimmed/Blurred Scrim (Escape 1)
        GestureDetector(
          onTap: widget.onClose,
          behavior: HitTestBehavior.opaque,
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
            child: Container(
              color: Colors.black.withOpacity(0.40),
            ),
          ),
        ),

        // Centered Floating VisionOS Glass Window
        SafeArea(
          child: Center(
            child: Container(
              constraints: const BoxConstraints(maxWidth: 520, maxHeight: 500),
              margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(28),
                child: BackdropFilter(
                  filter: ImageFilter.blur(sigmaX: 28, sigmaY: 28),
                  child: Container(
                    padding: const EdgeInsets.all(18),
                    decoration: BoxDecoration(
                      color: const Color(0x1EFFFFFF), // Pure visionOS translucent frosted glass
                      borderRadius: BorderRadius.circular(28),
                      border: Border.all(color: Colors.white.withOpacity(0.20), width: 0.5),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.25),
                          blurRadius: 36,
                          offset: const Offset(0, 14),
                        ),
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // Header with Vernacular: "Premium Theme Market" & Escape 2 (Circular Close Icon)
                        Row(
                          children: [
                            const Icon(Icons.wallpaper_rounded, size: 20, color: Colors.white),
                            const SizedBox(width: 8),
                            Text(
                              "Premium Theme Market",
                              style: SpatialTypography.windowTitle(
                                fontSize: 16,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            const Spacer(),
                            // Escape 2: Circular VisionOS Close Button with spring physics
                            VisionPressable(
                              onTap: widget.onClose,
                              borderRadius: BorderRadius.circular(16),
                              child: Container(
                                width: 28,
                                height: 28,
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  color: const Color(0x18FFFFFF),
                                  border: Border.all(color: Colors.white12, width: 0.5),
                                ),
                                child: const Center(
                                  child: Icon(Icons.close_rounded, size: 15, color: Colors.white70),
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 6),

                        // Subtitle
                        Text(
                          "Select high-fidelity spatial living backgrounds for your cosmos.",
                          style: SpatialTypography.caption(fontSize: 11, color: Colors.white60),
                        ),
                        const SizedBox(height: 10),

                        // ===== PERMANENT SEARCH BAR (Always Visible) =====
                        Container(
                          decoration: BoxDecoration(
                            color: const Color(0x18FFFFFF),
                            borderRadius: BorderRadius.circular(14),
                            border: Border.all(color: Colors.white.withOpacity(0.14), width: 0.5),
                          ),
                          child: TextField(
                            controller: _searchCtrl,
                            style: GoogleFonts.instrumentSans(fontSize: 11, color: Colors.white),
                            decoration: InputDecoration(
                              hintText: "Search themes by name or palette...",
                              hintStyle: GoogleFonts.instrumentSans(fontSize: 11, color: Colors.white38),
                              prefixIcon: const Icon(Icons.search_rounded, size: 16, color: Colors.white54),
                              suffixIcon: _searchQuery.isNotEmpty
                                  ? IconButton(
                                      icon: const Icon(Icons.close_rounded, size: 14, color: Colors.white54),
                                      onPressed: () {
                                        _searchCtrl.clear();
                                        setState(() => _searchQuery = '');
                                      },
                                    )
                                  : null,
                              isDense: true,
                              contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                              border: InputBorder.none,
                            ),
                            onChanged: (val) {
                              setState(() {
                                _searchQuery = val.trim();
                              });
                            },
                          ),
                        ),
                        const SizedBox(height: 12),

                        // Themes Grid
                        Expanded(
                          child: filteredThemes.isEmpty
                              ? Center(
                                  child: Text(
                                    _searchQuery.isEmpty
                                        ? "No themes available"
                                        : "No matching themes found",
                                    style: SpatialTypography.caption(fontSize: 11, color: Colors.white54),
                                  ),
                                )
                              : GridView.builder(
                                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                                    crossAxisCount: 3,
                                    crossAxisSpacing: 10,
                                    mainAxisSpacing: 10,
                                    childAspectRatio: 0.56,
                                  ),
                                  itemCount: filteredThemes.length,
                                  itemBuilder: (ctx, i) {
                                    final theme = filteredThemes[i];
                                    final isSelected = theme.id == widget.currentTheme.id;

                                    return VisionPressable(
                                      onTap: () {
                                        widget.onSelectTheme(theme);
                                      },
                                      borderRadius: BorderRadius.circular(14),
                                      child: Container(
                                        decoration: BoxDecoration(
                                          borderRadius: BorderRadius.circular(14),
                                          border: Border.all(
                                            color: isSelected ? Colors.white : Colors.white24,
                                            width: isSelected ? 1.5 : 0.5,
                                          ),
                                          boxShadow: isSelected
                                              ? [
                                                  BoxShadow(
                                                    color: Colors.white.withOpacity(0.30),
                                                    blurRadius: 10,
                                                    spreadRadius: 1,
                                                  )
                                                ]
                                              : null,
                                          image: DecorationImage(
                                            image: AssetImage(theme.assetPath),
                                            fit: BoxFit.cover,
                                            alignment: Alignment.center,
                                            filterQuality: FilterQuality.medium,
                                          ),
                                        ),
                                        alignment: Alignment.bottomCenter,
                                        child: Container(
                                          width: double.infinity,
                                          padding: const EdgeInsets.symmetric(vertical: 6),
                                          decoration: BoxDecoration(
                                            color: Colors.black.withOpacity(0.45),
                                            borderRadius: const BorderRadius.vertical(bottom: Radius.circular(12)),
                                          ),
                                          child: Text(
                                            theme.name,
                                            textAlign: TextAlign.center,
                                            style: GoogleFonts.instrumentSans(
                                              fontSize: 11,
                                              fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                                              color: Colors.white,
                                            ),
                                            maxLines: 1,
                                            overflow: TextOverflow.ellipsis,
                                          ),
                                        ),
                                      ),
                                    );
                                  },
                                ),
                        ),
                        const SizedBox(height: 10),

                        // Action Button (Escape 2)
                        Align(
                          alignment: Alignment.centerRight,
                          child: VisionPressable(
                            onTap: widget.onClose,
                            borderRadius: BorderRadius.circular(12),
                            child: Container(
                              padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 8),
                              decoration: BoxDecoration(
                                color: const Color(0x18FFFFFF),
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(color: Colors.white.withOpacity(0.15), width: 0.5),
                              ),
                              child: Text(
                                "Done",
                                style: GoogleFonts.instrumentSans(fontSize: 11, fontWeight: FontWeight.w600, color: Colors.white),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}
