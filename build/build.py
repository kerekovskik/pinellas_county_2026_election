#!/usr/bin/env python3
"""Assemble ../index.html from template.html + research/*.json + editorial/*.json.

Usage: python3 build/build.py   (run from anywhere; paths are relative to this file)
Edit the JSON files, not index.html, then rebuild."""
import json, re, sys, pathlib

SP = pathlib.Path(__file__).parent
R = SP / "research"
E = SP / "editorial"
REPO = SP.parent
MD = REPO / "pinellas-2026-general-election-ballot.md"

def load(p, default=None):
    if not p.exists():
        if default is not None:
            print(f"WARN missing {p.name}, using default", file=sys.stderr); return default
        sys.exit(f"missing {p}")
    with open(p) as f:
        return json.load(f)

# ---------- candidates ----------
candidates = []
for name in ["federal", "statewide", "legislature", "county", "municipal"]:
    data = load(R / f"{name}.json")
    for c in data: c.setdefault("_src", name)
    candidates += data

required = ["id","name","party","contest","category","alignment","alignmentBadge","polling","pollingStatus",
            "pollingDetails","raised","raisedNumeric","spentNumeric","backers","lgbtqStance","lgbtqBadge",
            "lgbtqDetails","platform","controversy","endorsements","sources"]
ids = set()
ALIGN = {"Progressive","Establishment","Conservative Establishment","Nonpartisan / Moderate","Independent / Third Party"}
LGBTQ = {"Vanguard","Consistent Support","Neutral / Standard","Opposed / Culture War"}
problems = []
for c in candidates:
    for k in required:
        if k not in c or c[k] in (None, ""):
            problems.append(f"{c.get('id','?')}: missing {k}")
    if c["id"] in ids: problems.append(f"duplicate id {c['id']}")
    ids.add(c["id"])
    if c.get("alignment") not in ALIGN: problems.append(f"{c['id']}: bad alignment {c.get('alignment')!r}")
    if c.get("lgbtqStance") not in LGBTQ: problems.append(f"{c['id']}: bad lgbtqStance {c.get('lgbtqStance')!r}")
    c.setdefault("incumbent", False); c.setdefault("primaryResult", "n/a")
    STD = {"Progressive": "🟢 Progressive", "Establishment": "🔵 Establishment", "Conservative Establishment": "🔴 Conservative / GOP",
           "Independent / Third Party": "🟡 Independent / Third Party", "Nonpartisan / Moderate": "⚪ Nonpartisan / Moderate"}
    STDL = {"Vanguard": "🏳️‍🌈 Outspoken Champion", "Consistent Support": "✅ Consistent Support", "Neutral / Standard": "⚖️ No Public Record", "Opposed / Culture War": "⚠️ Opposed / Culture War"}
    c.setdefault("alignmentNote", "")
    m = re.search(r"\((.*)\)\s*$", c["alignmentBadge"])
    if m: c["alignmentNote"] = m.group(1)
    c["alignmentBadge"] = STD[c["alignment"]]
    c["lgbtqBadge"] = STDL[c["lgbtqStance"]]
    c.pop("_src", None)
# Apply editorial overrides (fixes to agent output) if present
for ov in load(E / "overrides.json", default=[]):
    tgt = next((c for c in candidates if c["id"] == ov["id"]), None)
    if tgt is None: problems.append(f"override for unknown id {ov['id']}"); continue
    tgt.update({k: v for k, v in ov.items() if k != "id"})

# ---------- measures + full ballot text from markdown ----------
measures = load(R / "measures.json")
md = MD.read_text()
q_section = md.split("# Ballot Questions", 1)[1].split("# Key Dates", 1)[0]
texts = {}   # (scope, normalized number) -> text
order_in_scope = {}
scope = None
for block in re.split(r"\n(?=### |\*\*)", q_section):
    block = block.strip()
    if block.startswith("## "): 
        continue
    if block.startswith("### Amendment"):
        scope = "Statewide"
        head, _, body = block.partition("\n")
        num = head[4:].split(" — ")[0].strip()
        body = re.sub(r"^\*[^*]+\*\n\n", "", body.strip())          # drop italic article line
        body = re.split(r"\n- Yes", body)[0].strip()
        texts[("Statewide", num.lower())] = body
    elif block.startswith("### "):
        scope = block[4:].split("\n")[0].strip()
    elif block.startswith("**") and scope:
        head, _, body = block.partition("\n")
        num = head.strip("*").split(" — ")[0].strip()
        body = re.split(r"\n- Yes", body.strip())[0].strip()
        key = (scope, re.sub(r"[^a-z0-9 ]", "", num.lower()).strip())
        texts[key] = body
        order_in_scope.setdefault(scope, []).append(key)
def norm(s): return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()
for m in measures:
    key = (m["scope"], norm(m["number"]))
    if m["scope"] == "Statewide":
        key = ("Statewide", m["number"].lower().strip())
    txt = texts.get(key)
    if txt is None:
        # fallback: match by scope and digit
        digit = re.sub(r"\D", "", m["number"]) or "1"
        cands = [k for k in texts if k[0] == m["scope"] and (re.sub(r"\D", "", k[1]) or "1") == digit]
        if len(cands) == 1: txt = texts[cands[0]]
    if txt is None: problems.append(f"measure {m['id']}: no ballot text match for {key}")
    m["fullText"] = txt or ""
unmatched = [k for k in texts if not any(m.get("fullText") == texts[k] for m in measures)]
for k in unmatched: problems.append(f"ballot text not used: {k}")

judicial = load(R / "judicial.json")

# ---------- editorial ----------
pollCharts = load(E / "pollCharts.json", default=[])
pollInsights = load(E / "pollInsights.json", default=[])
finCharts = load(E / "finCharts.json", default=[])
finInsights = load(E / "finInsights.json", default=[])
controversies = load(E / "controversies.json", default=[])
contestNotes = load(E / "contestNotes.json", default={})
for k in controversies:
    if k.get("candidateId") and k["candidateId"] not in ids: problems.append(f"controversy refs unknown id {k['candidateId']}")

if problems:
    print("PROBLEMS:\n  " + "\n  ".join(problems), file=sys.stderr)
    if "--force" not in sys.argv: sys.exit(1)

def js(obj): return json.dumps(obj, ensure_ascii=False, indent=4).replace("</", "<\\/")
tpl = (SP / "template.html").read_text()
out = tpl
for ph, val in [("CANDIDATES", candidates), ("MEASURES", measures), ("JUDICIAL", judicial), ("POLLCHARTS", pollCharts),
                ("POLLINSIGHTS", pollInsights), ("FINCHARTS", finCharts), ("FININSIGHTS", finInsights),
                ("CONTROVERSIES", controversies), ("CONTESTNOTES", contestNotes)]:
    marker = f"/*__{ph}__*/"
    assert marker in out, marker
    out = out.replace(marker, js(val))
(REPO / "index.html").write_text(out)
print(f"OK: {len(candidates)} candidates, {len(measures)} measures ({sum(1 for m in measures if m['fullText'])} with text), {len(judicial)} judges -> index.html ({len(out):,} bytes)")
