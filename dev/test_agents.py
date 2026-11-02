# Made by Claude (2026-10-23). Checks the consensus agent and the Smart Gen agent read what the agent model returns,
# with the model's reply stood in (no keys spent), on a copy of the data folder.
import json, os, shutil, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.path.join(ROOT, "dev", "online_test", "data_agents")
shutil.rmtree(TMP, ignore_errors=True)
os.makedirs(TMP)
shutil.copy(os.path.join(ROOT, "data", "collider_config.json"), TMP)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import collider_config as ccfg, collider_server as cs  # noqa
cfg = ccfg.load(TMP)
cs.setup(ROOT, os.path.join(ROOT, "build", "web"), TMP, 47994, cfg)
print("instruction is David's:", cs.AGENT_PROMPT.startswith("Inputs:"), "| old keys gone:",
      not any(k in cs.CONFIG for k in ("lines_prompt", "essence_prompt", "line_rule")))
seen = {}


def fake(agent, msgs, *a, **k):
    seen["system"] = msgs[0]["content"]
    if "Smart Gen holds" in msgs[0]["content"]:
        return json.dumps({"create": [{"type": "reminder", "title": "Call the dentist", "content": "", "due": "Friday 3 PM", "project": ""}], "update": []})
    return json.dumps({"need": "know the boiling point", "sentiments": {"R1": "Water boils at 100 C at sea level", "R2": "Water boils at 100 C at sea level", "R3": "It depends on altitude"},
                       "groups": [["R1", "R2"], ["R3"]], "consensus": "Water boils at 100 C at sea level", "chains": {"R1": 3, "R2": 5, "R3": 2}})


cs.call_model = fake
c = cs.run_consensus("At what temperature does water boil?", {"a": "x", "b": "y", "c": "z"}, 115)
print("score", c["score"], "| summary", c["summary"], "| lines", c["lines"], "| consensus chain", c["consensus_chain"], "| dissent", c["dissent"])
cs._smartgen_mem = []
cs.SMARTGEN_FILE = os.path.join(TMP, "smartgen_cards.json")
cs._smartgen_agent({"id": "j1", "prompt": "remind me to call the dentist friday at 3", "results": {"a": {"status": "done", "text": "Sure."}}})
print("smart gen items", [(x["type"], x["title"], x["due"]) for x in cs._smartgen_mem])
