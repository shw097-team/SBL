import json, os, sys
root = sys.argv[1]
os.chdir(root)
d = json.load(open("MANIFEST.json", encoding="utf-8"))
print("files", len(d["files"]), "expected", len(d["expected_entry_set"]))
on = set()
for dp, dns, fns in os.walk("."):
    dns[:] = [x for x in dns if x not in {".git", "__pycache__"}]
    for fn in fns:
        if fn in {"MANIFEST.json", "PROVENANCE.json", "SHA256SUMS"}:
            continue
        on.add(os.path.relpath(os.path.join(dp, fn), ".").replace("\\", "/"))
print("ondisk", len(on))
declared = set(e["path"] for e in d["files"])
print("ondisk-not-manifest", sorted(on - declared))
print("manifest-not-ondisk", sorted(declared - on))
