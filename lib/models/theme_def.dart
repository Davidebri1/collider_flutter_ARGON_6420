import '../core/media/theme_cloud.dart';

class AmbientTrack {
  final int number;
  final String title;
  final String duration;
  final String mood;

  /// The recording itself, for songs that come from the Cloudflare bucket.
  final String? audioUrl;

  const AmbientTrack({
    required this.number,
    required this.title,
    required this.duration,
    this.mood = 'Ambient',
    this.audioUrl,
  });
}

class WallpaperTheme {
  final String id;
  final String name;
  final String assetPath;
  /// Optional looping live wallpaper (mp4 under assets/themes/premium/live/<slug>/).
  final String? videoPath;
  final bool isPremium;
  final String creator;
  final String tier;
  final String collection;
  final List<AmbientTrack> tracks;
  final String? productId;
  final String? priceLabel;

  const WallpaperTheme({
    required this.id,
    required this.name,
    required this.assetPath,
    this.videoPath,
    this.isPremium = false,
    this.creator = 'Studio Nebula',
    this.tier = 'Standard Spatial',
    this.collection = 'Spatial Ambient Series',
    this.productId,
    this.priceLabel,
    this.tracks = const [],
  });
}

class WallpaperCatalog {
  static const List<WallpaperTheme> freeThemes = [
    WallpaperTheme(
      id: 'visionos_living_room',
      name: 'VisionOS Spatial Room',
      assetPath: 'https://collider-media.ebridavid.workers.dev/free/visionos_living_room.png',
      creator: 'Apple Design Lab',
      tier: 'Free Spatial Canvas',
    ),
    WallpaperTheme(
      id: 'starbridge',
      name: 'Star Bridge',
      assetPath: 'https://collider-media.ebridavid.workers.dev/free/starbridge.jpg',
      creator: 'Studio Nebula',
      tier: 'Free Spatial Canvas',
    ),
    WallpaperTheme(
      id: 'sanctuary_free',
      name: 'Sanctuary Still',
      assetPath: 'https://collider-media.ebridavid.workers.dev/free/sanctuary.jpg',
      creator: 'Aethelgard Audio',
      tier: 'Free Spatial Canvas',
    ),
    WallpaperTheme(
      id: 'observatory_free',
      name: 'Observatory',
      assetPath: 'https://collider-media.ebridavid.workers.dev/free/observatory.jpg',
      creator: 'Kepler Dynamics',
      tier: 'Free Spatial Canvas',
    ),
    WallpaperTheme(
      id: 'ocean_free',
      name: 'Deep Ocean Still',
      assetPath: 'https://collider-media.ebridavid.workers.dev/free/ocean.jpg',
      creator: 'Abyssal Sound',
      tier: 'Free Spatial Canvas',
    ),
    WallpaperTheme(
      id: 'garden',
      name: 'Ethereal Garden',
      assetPath: 'https://collider-media.ebridavid.workers.dev/free/garden.jpg',
      creator: 'Flora Sonics',
      tier: 'Free Spatial Canvas',
    ),
    WallpaperTheme(
      id: 'neoncity_free',
      name: 'Neon City Still',
      assetPath: 'https://collider-media.ebridavid.workers.dev/free/neoncity.jpg',
      creator: 'Synthwave Matrix',
      tier: 'Free Spatial Canvas',
    ),
    WallpaperTheme(
      id: 'rainfall',
      name: 'Night Rainfall',
      assetPath: 'https://collider-media.ebridavid.workers.dev/free/rainfall.jpg',
      creator: 'Hydrophonic Labs',
      tier: 'Free Spatial Canvas',
    ),
    WallpaperTheme(
      id: 'transit',
      name: 'Hyper Transit',
      assetPath: 'https://collider-media.ebridavid.workers.dev/free/transit.jpg',
      creator: 'MagLev Acoustics',
      tier: 'Free Spatial Canvas',
    ),
    WallpaperTheme(
      id: 'dunehall',
      name: 'Dune Hall',
      assetPath: 'https://collider-media.ebridavid.workers.dev/free/dunehall.jpg',
      creator: 'Arrakis Wind Collective',
      tier: 'Free Spatial Canvas',
    ),
  ];

  /// The live wallpapers: David's Cloudflare bucket "collider-themes" (ThemeCloud). Nothing is built into the app;
  /// the last list read is kept on the device so the market opens at once.
  static List<WallpaperTheme> get premiumThemes => ThemeCloud.instance.themes;

  /// A theme's songs. The live wallpapers carry their own (the bucket's songs); a built-in theme takes five of the
  /// bucket's songs, a different five for each theme. Made by Claude (2026-10-18), replacing the made-up titles.
  static List<AmbientTrack> tracksFor(WallpaperTheme t) {
    if (t.tracks.isNotEmpty) return t.tracks;
    final seen = <String>{};
    final pool = <AmbientTrack>[
      for (final c in ThemeCloud.instance.themes)
        for (final a in c.tracks)
          if (a.audioUrl != null && seen.add(a.audioUrl!)) a,
    ];
    if (pool.isEmpty) return const [];
    final start = (freeThemes.indexWhere((f) => f.id == t.id).clamp(0, 999) * 5) % pool.length;
    return [
      for (int i = 0; i < 5 && i < pool.length; i++)
        AmbientTrack(number: i + 1, title: pool[(start + i) % pool.length].title, duration: '', mood: '', audioUrl: pool[(start + i) % pool.length].audioUrl),
    ];
  }



  static WallpaperTheme defaultTheme = freeThemes[1];
}
