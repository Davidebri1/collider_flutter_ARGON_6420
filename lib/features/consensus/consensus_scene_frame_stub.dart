import 'package:flutter/widgets.dart';

class ConsensusSceneFrame extends StatelessWidget {
  final String html;
  final String payloadJson;
  final VoidCallback? onClose;
  final ValueChanged<bool>? onLabelsChange;
  final ValueChanged<String>? onTabChange;

  const ConsensusSceneFrame({
    super.key,
    required this.html,
    required this.payloadJson,
    this.onClose,
    this.onLabelsChange,
    this.onTabChange,
  });

  @override
  Widget build(BuildContext context) => const SizedBox.expand();
}
