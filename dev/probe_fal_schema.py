# Made by Claude (2026-10-20). Reads the inputs and outputs fal documents for the given models (no generation, no cost).
import json, sys, urllib.parse, urllib.request
for eid in sys.argv[1:]:
    url = "https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=" + urllib.parse.quote(eid, safe="")
    try:
        d = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Collider/1.0"}), timeout=40).read())
    except Exception as e:
        print(eid, "ERR", e)
        continue
    schemas = d.get("components", {}).get("schemas", {})
    print("==", eid)
    for name, s in schemas.items():
        if not (name.endswith("Input") or name.endswith("Output")):
            continue
        props = s.get("properties", {})
        print(" ", name, "required:", s.get("required"))
        for k, v in props.items():
            desc = (v.get("description") or "")[:90].replace("\n", " ")
            print("    ", k, v.get("type") or v.get("$ref") or v.get("anyOf"), "default:", v.get("default"), "enum:", v.get("enum"), "|", desc)
