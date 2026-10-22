import json

q = json.load(open(r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2/QUEUE_R15_2.json",
                   encoding="utf-8"))
for i in q["items"]:
    blob = json.dumps(i, ensure_ascii=False)
    if "w15_gate" in blob or "w15" in str(i.get("id", "")).lower():
        print(json.dumps({k: i.get(k) for k in ("id", "status", "required_lane", "lane_receipt_file",
                                                "kind", "title", "owner")}, ensure_ascii=False, indent=2))
