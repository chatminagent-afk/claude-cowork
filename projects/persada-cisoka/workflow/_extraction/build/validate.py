# -*- coding: utf-8 -*-
import json, os, re

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
FILES = [
    '2026-07-17-VIRA-PCR-main.json',
    '2026-07-17-VIRA-PCR-buffer-cleanup.json',
    '2026-07-17-VIRA-PCR-error-notifier.json',
]

def load(p):
    with open(p, 'r', encoding='utf-8') as f:
        return f.read()

results = []
for fn in FILES:
    path = os.path.join(OUT, fn)
    raw = load(path)
    print("=" * 70)
    print("FILE:", fn)
    # 1. parse valid
    try:
        wf = json.loads(raw)
        print("  [1] JSON parse: OK")
    except Exception as e:
        print("  [1] JSON parse: FAIL", e); continue

    nodes = wf.get("nodes", [])
    node_names = set(n["name"] for n in nodes)
    print("      node count:", len(nodes))

    # 2. semua node di connections ada di nodes
    conn = wf.get("connections", {})
    missing = set()
    for src, types in conn.items():
        if src not in node_names:
            missing.add("SRC:" + src)
        for typ, outs in types.items():
            for out in outs:
                for c in out:
                    if c["node"] not in node_names:
                        missing.add("TGT:" + c["node"])
    print("  [2] connections refs:", "OK" if not missing else ("FAIL " + str(missing)))

    # 3. semua $('NamaNode') di jsCode/expression ada di nodes
    refs = set(re.findall(r"\$\(\\?'([^'\\]+)\\?'\)", raw))
    refs |= set(re.findall(r"\$\('([^']+)'\)", raw))
    unknown_refs = sorted(r for r in refs if r not in node_names)
    print("  [3] $('node') refs:", "OK" if not unknown_refs else ("MISSING " + str(unknown_refs)))

    # 6. struktur top-level
    need = ["name", "nodes", "connections", "settings"]
    tl = [k for k in need if k not in wf]
    print("  [6] top-level keys:", "OK" if not tl else ("MISSING " + str(tl)))
    results.append((fn, wf, raw, node_names))

# 4 & 5. grep sisa lintas semua file
print("=" * 70)
combined = "\n".join(load(os.path.join(OUT, fn)) for fn in FILES)
for term in ["sam", "scholars", "program", "kelas_anak", "gform"]:
    hits = len(re.findall(term, combined, re.IGNORECASE))
    # tampilkan konteks unik
    ctx = set()
    for m in re.finditer(term, combined, re.IGNORECASE):
        s = max(0, m.start()-25); e = min(len(combined), m.end()+25)
        ctx.add(combined[s:e].replace("\n", " "))
    print(f"  [4] grep '{term}': {hits} hit(s)")
    for c in list(ctx)[:6]:
        print("        ...", c)

# 5. secret/token/nomor produksi
print("-" * 40)
for term in ["KM40LI0426", "4efe3780e1c0b53c", "D-4ZV1F", "6285155202354", "6596110395",
             "1tEJYayS0pQTVO2FI9xO363", "3gTKMbD8lJDLbRqR", "DPNnlN1bTbbMf8ks"]:
    hits = len(re.findall(re.escape(term), combined))
    print(f"  [5] secret '{term}': {hits} hit(s)")
