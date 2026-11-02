import 'package:material_ui/material_ui.dart';

enum ModelCategory { general, image, video, audio, writing }
enum ModelTier { free, pro, elite }

class ModelDef {
  final String id;
  final String label;
  final String short;
  final String desc;
  final ModelTier tier;
  final List<ModelCategory> categories;
  final Color providerColor;
  final bool isMedia;

  const ModelDef({
    required this.id,
    required this.label,
    required this.short,
    required this.desc,
    required this.tier,
    required this.categories,
    required this.providerColor,
    this.isMedia = false,
  });
}

class ModelRoster {
  static const List<ModelDef> _seed = [
    // General - Free
    ModelDef(
      id: 'free/gemini-3-6-flash-lite',
      label: 'Gemini 3.6 Flash Lite',
      short: 'G36L',
      desc: 'Google lightweight flash reasoning engine.',
      tier: ModelTier.free,
      categories: [ModelCategory.general],
      providerColor: Color(0xFF7FD8C4),
    ),
    ModelDef(
      id: 'free/gpt-5-nano',
      label: 'GPT-5 Nano',
      short: 'G5N',
      desc: 'OpenAI ultra-fast responsive mini engine.',
      tier: ModelTier.free,
      categories: [ModelCategory.general],
      providerColor: Color(0xFF10B981),
    ),
    ModelDef(
      id: 'free/mistral-small',
      label: 'Mistral Small 3.2',
      short: 'MS3',
      desc: 'Mistral efficient high-throughput reasoning.',
      tier: ModelTier.free,
      categories: [ModelCategory.general],
      providerColor: Color(0xFFF97316),
    ),
    ModelDef(
      id: 'free/qwen-3-6-27b',
      label: 'Qwen 3.6 27B',
      short: 'QW36',
      desc: 'Alibaba high-performance general model.',
      tier: ModelTier.free,
      categories: [ModelCategory.general],
      providerColor: Color(0xFF6366F1),
    ),
    ModelDef(
      id: 'free/minimax-m3',
      label: 'MiniMax M3',
      short: 'MM3',
      desc: 'MiniMax flagship with 1M context window.',
      tier: ModelTier.free,
      categories: [ModelCategory.general],
      providerColor: Color(0xFFF97316),
    ),
    ModelDef(
      id: 'free/grok-3-mini',
      label: 'Grok 3 Mini',
      short: 'GrokM',
      desc: 'xAI rapid reasoning model with real-time knowledge.',
      tier: ModelTier.free,
      categories: [ModelCategory.general],
      providerColor: Color(0xFFEF4444),
    ),
    ModelDef(
      id: 'free/deepseek-v3',
      label: 'DeepSeek V3',
      short: 'DS-V3',
      desc: 'DeepSeek MoE generalist with sparse attention.',
      tier: ModelTier.free,
      categories: [ModelCategory.general],
      providerColor: Color(0xFF0EA5E9),
    ),
    ModelDef(
      id: 'free/llama-3-3-70b',
      label: 'Llama 3.3 70B',
      short: 'L70B',
      desc: 'Meta open-weights flagship general reasoning.',
      tier: ModelTier.free,
      categories: [ModelCategory.general],
      providerColor: Color(0xFF3B82F6),
    ),

    // Advanced Writing & Analysis - Pro & Elite
    ModelDef(
      id: 'pro/claude-3-7-sonnet',
      label: 'Claude 3.7 Sonnet',
      short: 'Sonnet',
      desc: 'Anthropic deep reasoning & thoughtful synthesis.',
      tier: ModelTier.pro,
      categories: [ModelCategory.general, ModelCategory.writing],
      providerColor: Color(0xFFD97706),
    ),
    ModelDef(
      id: 'pro/deepseek-r1',
      label: 'DeepSeek R1',
      short: 'DS-R1',
      desc: 'DeepSeek open reasoning engine with structured problem breakdown.',
      tier: ModelTier.pro,
      categories: [ModelCategory.general, ModelCategory.writing],
      providerColor: Color(0xFF0284C7),
    ),
    ModelDef(
      id: 'pro/mistral-large',
      label: 'Mistral Large',
      short: 'MLg',
      desc: 'Mistral high-fidelity editorial and comprehensive analysis.',
      tier: ModelTier.pro,
      categories: [ModelCategory.general, ModelCategory.writing],
      providerColor: Color(0xFFEA580C),
    ),
    ModelDef(
      id: 'pro/gpt-4o',
      label: 'GPT-4o Omni',
      short: 'GPT-4o',
      desc: 'OpenAI multi-modal high-intelligence model.',
      tier: ModelTier.pro,
      categories: [ModelCategory.general, ModelCategory.writing],
      providerColor: Color(0xFF059669),
    ),

    // Generative Media - Image
    ModelDef(
      id: 'image/flux-1-1-pro',
      label: 'FLUX 1.1 Pro',
      short: 'FLUX',
      desc: 'High-coherence 3D visual and photorealistic synthesis.',
      tier: ModelTier.pro,
      categories: [ModelCategory.image],
      providerColor: Color(0xFF06B6D4),
      isMedia: true,
    ),
    ModelDef(
      id: 'image/midjourney-v6',
      label: 'Midjourney v6.1',
      short: 'MJ',
      desc: 'Artistic photorealistic generative studio.',
      tier: ModelTier.pro,
      categories: [ModelCategory.image],
      providerColor: Color(0xFFA855F7),
      isMedia: true,
    ),

    // Generative Media - Video
    ModelDef(
      id: 'video/kling-video',
      label: 'Kling 1.5 Video',
      short: 'Kling',
      desc: 'Temporal cinematic text-to-video generator.',
      tier: ModelTier.elite,
      categories: [ModelCategory.video],
      providerColor: Color(0xFFF43F5E),
      isMedia: true,
    ),
    ModelDef(
      id: 'video/runway-gen3',
      label: 'Runway Gen-3 Alpha',
      short: 'Runway',
      desc: 'High-fidelity cinematic motion video engine.',
      tier: ModelTier.elite,
      categories: [ModelCategory.video],
      providerColor: Color(0xFF8B5CF6),
      isMedia: true,
    ),

    // Audio & Music
    ModelDef(
      id: 'audio/suno-v4',
      label: 'Suno v4 Music',
      short: 'Suno',
      desc: 'Full-track studio song and vocal production.',
      tier: ModelTier.pro,
      categories: [ModelCategory.audio],
      providerColor: Color(0xFFEC4899),
      isMedia: true,
    ),
    ModelDef(
      id: 'audio/udio-1-5',
      label: 'Udio 1.5 Pro',
      short: 'Udio',
      desc: 'High-definition instrumental and vocal music generator.',
      tier: ModelTier.pro,
      categories: [ModelCategory.audio],
      providerColor: Color(0xFF14B8A6),
      isMedia: true,
    ),
    ModelDef(
      id: 'audio/elevenlabs-music',
      label: 'ElevenLabs Audio',
      short: '11Labs',
      desc: 'Ultra-realistic voice cloning and ambient soundtrack studio.',
      tier: ModelTier.pro,
      categories: [ModelCategory.audio],
      providerColor: Color(0xFFF59E0B),
      isMedia: true,
    ),
  ];

  /// Live roster. Starts from the seed; replaced by the server's models at launch.
  static List<ModelDef> allModels = [for (final m in _seed) if (!m.isMedia) m];

  /// Live text models from the Collider server replace the seed text models.
  /// Media models stay listed under their own categories.
  static void setLive(List<ModelDef> live) {
    // The seed's media models were names with nothing behind them; the live picture models come from the server.
    allModels = [...live];
  }

  static List<ModelDef> forCategory(ModelCategory category) {
    return allModels.where((m) => m.categories.contains(category)).toList();
  }

  static ModelDef? byId(String id) {
    try {
      return allModels.firstWhere((m) => m.id == id);
    } catch (_) {
      return null;
    }
  }
}
