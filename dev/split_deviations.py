# Made by Claude (2026-10-20). Moves the old deviations list, which had become a log of changes, to docs\CHANGES.md
# word for word, so nothing is lost; docs\DEVIATIONS.md is then rewritten with true departures only.
import os
docs = os.path.join(os.path.dirname(__file__), "..", "docs")
old = open(os.path.join(docs, "DEVIATIONS.md"), encoding="utf-8").read()
head = ("# Changes (Claude's log)\n\n"
        "Made by Claude on 2026-10-20 from the old deviations list (D1 to D74), kept here word for word.\n"
        "Most of those entries were changes David asked for, or asset choices, not departures from a reference or spec;\n"
        "David, 20 Oct: \"I think you got the intent of deviations wrong.\" The true departures are in DEVIATIONS.md.\n\n---\n\n")
open(os.path.join(docs, "CHANGES.md"), "w", encoding="utf-8", newline="").write(head + old)
print("CHANGES.md", len(head + old))
