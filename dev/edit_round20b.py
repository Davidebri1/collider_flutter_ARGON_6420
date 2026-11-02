# Made by Claude (2026-10-21). Round 20b: the opened summary stays in view at the top of its conversation; an attached
# conversation has no header of its own (its summary is the header), its menu sits at the left of the entry box.
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent


def edit(rel, pairs):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        if s.count(old) != 1:
            sys.exit(f"{rel}: expected one match for {old[:70]!r} (found {s.count(old)})")
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8")
    print("edited", rel)


edit("lib/main.dart", [
    ("""                      ModelPill(
                        item: activePills[i],
                        elevation: activePills.length <= 1 ? 1.0 : 1.0 - i / (activePills.length - 1),
                        isExpanded: activePills[i].modelDef.id == openId,
                        onToggleExpand: () => _onTogglePill(activePills[i].modelDef.id),
                      ),""",
     """                      // the summary and the conversation it opens are one piece, scrolled into view together
                      Column(
                        key: activePills[i].modelDef.id == openId ? _openKey : null,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                      ModelPill(
                        item: activePills[i],
                        elevation: activePills.length <= 1 ? 1.0 : 1.0 - i / (activePills.length - 1),
                        isExpanded: activePills[i].modelDef.id == openId,
                        onToggleExpand: () => _onTogglePill(activePills[i].modelDef.id),
                      ),"""),
    ("""                            ? Padding(
                                key: _openKey,
                                padding: const EdgeInsets.only(top: 8),
                                child: SizedBox(height: convHeight, child: conversation),
                              )
                            : const SizedBox(width: double.infinity),
                      ),""",
     """                            ? Padding(
                                padding: const EdgeInsets.only(top: 8),
                                child: SizedBox(height: convHeight, child: conversation),
                              )
                            : const SizedBox(width: double.infinity),
                      ),
                        ],
                      ),"""),
    ("curve: Curves.easeOutCubic, alignment: 0.5);", "curve: Curves.easeOutCubic, alignment: 0.0);"),
])

edit("lib/features/ticker/widgets/conversation_view.dart", [
    ("""        // 0:639 header: the name, and a round button at the right.
        Padding(""",
     """        // 0:639 header: the name, and a round button at the right. Attached under its summary, there is none.
        if (!widget.attached)
        Padding("""),
    ("""          padding: const EdgeInsets.fromLTRB(14, 0, 4, 0),
          child: SizedBox(
            height: 40,
            child: Row(
              children: [
                Expanded(""",
     """          padding: EdgeInsets.fromLTRB(widget.attached ? 4 : 14, 0, 4, 0),
          child: SizedBox(
            height: 40,
            child: Row(
              children: [
                if (widget.attached) ...[
                  Builder(builder: (c) => VCircleButton(icon: Icons.more_horiz_rounded, size: 32, tooltip: 'More', onTap: () => _menu(c))),
                  const SizedBox(width: 6),
                ],
                Expanded("""),
])
