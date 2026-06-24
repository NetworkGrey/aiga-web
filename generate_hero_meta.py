#!/usr/bin/env python3
"""
generate_hero_meta.py
=====================
Reads hero data from the AIGA Knowledge Base Airtable base and writes
a fresh HERO_META JavaScript constant to AIGA_WP_Widget.html.

Usage:
    AIRTABLE_API_KEY=your_key python generate_hero_meta.py [--dry-run]

Options:
    --dry-run    Print the generated JS to stdout instead of writing to file.
    --output     Path to the widget HTML file (default: auto-detects from repo root).

Environment variables:
    AIRTABLE_API_KEY    Required. Your Airtable personal access token.
    AIRTABLE_BASE_ID    Optional. Overrides the default base ID.

Airtable base: AIGA Knowledge Base (appD9c9ONZGNcgnq1)
Table: Heroes (tblBTohOcVLUKKhJ8)
Rings table: Rings (tbllDKaFx8wh4TpM7) -- resolves linked ring names for
HERO_META, and also exports a RING_POOL constant of pool-allocation
suitability data. The cascade allocation logic itself runs at query time
in app.py, not here -- this script only exports the pool, it does not
assign rings to heroes.

Field ID map (from list_tables_for_base output):
  Name             fldjwHFmQKzKu1s4v  singleLineText
  Type             fld39hloCOq4Kw507  multipleSelects
  Rarity           fldAAEYZ023m1wApS  singleSelect
  Season           fld1lrjDbLkS09FZW  singleLineText
  Role             fld43lU9NUaf9sGXP  singleLineText
  Skill1           fldNXxq2FgIGJVIxT  singleLineText
  Skill2           fldTGfvzcln4lowxl  singleLineText
  Skill3 Rec       fldZxFZW6h7Efux6b  singleLineText
  Skill4 Rec       fldRkDxVWSX5iDZ0J  multipleSelects
  Skill Pool       fldIINIVqQWWEAE1M  multipleSelects
  Ring T0          fldSUhJQEB1gOBpZS  multipleRecordLinks -> Rings
  Ring T1          fld2jAIh9BShadM13  multipleRecordLinks -> Rings
  Ring T2          fld7y1eBeHlAxo60i  multipleRecordLinks -> Rings
  Mount Temp       fld5mpoP8CPc9rHmO  singleSelect
  Mount Trait 1    fldNkvsqF3GwvwIVo  singleLineText
  Mount Trait 2    fldG6Jn32lZL0hofC  singleLineText
  Adornment Form   fldRRvKyctnaWK890  singleSelect
  Pairings         fldwn0BheYYzLQgl2  singleLineText
  Data Status      fldICAkHKI5NFroeh  singleSelect
  Notes            fld7vH9oQpm5JdgBd  multilineText

Rings table fields (from list_tables_for_base output):
  Ring Name        fldIi2LvUz6PybBtF  singleLineText
  Tier             fldwHCQkDc4pDMa4l  singleSelect (T0/T1/T2)
  Suits Role(s)    fldNpjqtn6OGX8wGS  multipleSelects
  Suits Troop(s)   fldQem8XyrW9pgenW  multipleSelects
  Priority Rank    fldsEISuRO7CDGwkv  singleLineText
  Wrong For        flduLS40DhZ7cLft3  multilineText
  FTP Rating       fldk2wY18WiRRsFAn  singleSelect
  Meta Override    fldbXiKwsrqyqCDp1  checkbox

  DEPRECATED -- not read by this script. The pool-based model above is
  now authoritative for ring suitability:
  Assigned To Hero(es)  fldgHj8BPsPyVQ8Xx  multipleRecordLinks
"""

import os
import sys
import json
import re
import requests
from pathlib import Path
from typing import Optional

# ── Config ────────────────────────────────────────────────────────────────────
BASE_ID       = os.environ.get("AIRTABLE_BASE_ID", "appD9c9ONZGNcgnq1")
HEROES_TABLE  = "tblBTohOcVLUKKhJ8"
RINGS_TABLE   = "tbllDKaFx8wh4TpM7"
API_KEY       = os.environ.get("AIRTABLE_API_KEY", "")
API_BASE      = "https://api.airtable.com/v0"

DRY_RUN       = "--dry-run" in sys.argv

# Auto-detect widget path: look upward from this script for the repo root
def find_widget(start: Path) -> Path:
    for parent in [start, *start.parents]:
        candidate = parent / "AIGA_WP_Widget.html"
        if candidate.exists():
            return candidate
        candidate = parent / "static" / "AIGA_WP_Widget.html"
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "Could not find AIGA_WP_Widget.html. "
        "Run from inside the aiga-web repo, or pass --output <path>."
    )

# Allow explicit --output override
output_path = None
for i, arg in enumerate(sys.argv):
    if arg == "--output" and i + 1 < len(sys.argv):
        output_path = Path(sys.argv[i + 1])

if output_path is None and not DRY_RUN:
    output_path = find_widget(Path(__file__).resolve().parent)

# ── Airtable helpers ──────────────────────────────────────────────────────────
def at_headers():
    if not API_KEY:
        print("ERROR: AIRTABLE_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)
    return {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

def fetch_all(table_id: str, fields: Optional[list[str]] = None) -> list[dict]:
    """Fetch all records from an Airtable table, handling pagination."""
    records = []
    params = {"pageSize": 100, "returnFieldsByFieldId": "true"}
    if fields:
        params["fields[]"] = fields
    url = f"{API_BASE}/{BASE_ID}/{table_id}"

    while True:
        resp = requests.get(url, headers=at_headers(), params=params)
        if resp.status_code != 200:
            print(f"ERROR {resp.status_code}: {resp.text}", file=sys.stderr)
            sys.exit(1)
        data = resp.json()
        records.extend(data.get("records", []))
        offset = data.get("offset")
        if not offset:
            break
        params["offset"] = offset

    return records

# ── Fetch rings ────────────────────────────────────────────────────────────────
def fetch_rings() -> list[dict]:
    """Fetches every record in the Rings table (full fields)."""
    print("Fetching Rings table...", file=sys.stderr)
    records = fetch_all(RINGS_TABLE)
    print(f"  {len(records)} ring records fetched.", file=sys.stderr)
    return records

def build_ring_lookup(ring_records: list[dict]) -> dict[str, str]:
    """Returns {record_id: ring_name} for every ring in the Rings table."""
    lookup = {}
    for rec in ring_records:
        name = rec.get("fields", {}).get("fldIi2LvUz6PybBtF", "")
        if name:
            lookup[rec["id"]] = name
    print(f"  {len(lookup)} rings loaded.", file=sys.stderr)
    return lookup

def multiselect_names(raw) -> list[str]:
    """Normalizes a multipleSelects field value to a list of option-name strings."""
    if not raw:
        return []
    if isinstance(raw, str):
        raw = [raw]
    return [s if isinstance(s, str) else s.get("name", "") for s in raw]

def select_name(raw) -> str:
    """Normalizes a singleSelect field value to its option name."""
    if not raw:
        return ""
    return raw if isinstance(raw, str) else raw.get("name", "")

# ── Build ring pool: suitability data for the pool-based allocation model ─────
def build_ring_pool(ring_records: list[dict]) -> list[dict]:
    """Returns a list of {name, tier, suits_roles, suits_troops, priority_rank,
    wrong_for, ftp_rating, meta_override} for every ring -- the cascade
    allocation logic itself runs at query time in app.py, this just
    exports the pool's raw suitability data."""
    pool = []
    for rec in ring_records:
        f = rec.get("fields", {})
        name = f.get("fldIi2LvUz6PybBtF", "") or ""
        if not name.strip():
            continue
        pool.append({
            "name":          name,
            "tier":          select_name(f.get("fldwHCQkDc4pDMa4l")),
            "suits_roles":   multiselect_names(f.get("fldNpjqtn6OGX8wGS")),
            "suits_troops":  multiselect_names(f.get("fldQem8XyrW9pgenW")),
            "priority_rank": f.get("fldsEISuRO7CDGwkv", "") or "",
            "wrong_for":     f.get("flduLS40DhZ7cLft3", "") or "",
            "ftp_rating":    select_name(f.get("fldk2wY18WiRRsFAn")),
            "meta_override": bool(f.get("fldbXiKwsrqyqCDp1", False)),
        })
    print(f"  {len(pool)} rings in pool.", file=sys.stderr)
    return pool

def resolve_ring(linked_ids: list, ring_lookup: dict) -> str:
    """Resolve a list of linked record IDs to the first ring name."""
    if not linked_ids:
        return ""
    return ring_lookup.get(linked_ids[0], "")

# ── Fetch heroes ──────────────────────────────────────────────────────────────
def fetch_heroes(ring_lookup: dict) -> list[dict]:
    print("Fetching Heroes table...", file=sys.stderr)
    records = fetch_all(HEROES_TABLE)
    print(f"  {len(records)} hero records fetched.", file=sys.stderr)

    heroes = []
    for rec in records:
        f = rec.get("fields", {})

        # Skip junk rows: blank records, or template/header rows where the
        # Name field literally contains the field's own label ("Name").
        name_val = f.get("fldjwHFmQKzKu1s4v", "") or ""
        if not name_val.strip() or name_val.strip() == "Name":
            continue

        # Type: multipleSelects -> slash-joined string e.g. "CAV/ARC"
        type_vals = f.get("fld39hloCOq4Kw507", [])
        hero_type = "/".join(type_vals) if type_vals else ""

        # Rarity: singleSelect -> {name: "Legendary"}
        rarity_obj = f.get("fldAAEYZ023m1wApS", {})
        rarity = rarity_obj if isinstance(rarity_obj, str) else rarity_obj.get("name", "") if rarity_obj else ""

        # Mount Temperament: singleSelect
        temp_obj = f.get("fld5mpoP8CPc9rHmO", {})
        mount_temp = temp_obj if isinstance(temp_obj, str) else temp_obj.get("name", "") if temp_obj else ""

        # Adornment Form: singleSelect
        adorn_obj = f.get("fldRRvKyctnaWK890", {})
        adorn = adorn_obj if isinstance(adorn_obj, str) else adorn_obj.get("name", "") if adorn_obj else ""

        # Data Status: singleSelect
        status_obj = f.get("fldICAkHKI5NFroeh", {})
        status = status_obj if isinstance(status_obj, str) else status_obj.get("name", "") if status_obj else ""

        # Skill Pool: multipleSelects -> list of skill name strings
        # Use `or []` instead of a .get() default: .get(key, []) only falls
        # back when the key is missing, not when Airtable returns it present
        # but falsy (null/"") -- which silently produced an empty skills[]
        # for records edited shortly after this field was added.
        skills_raw = f.get("fldIINIVqQWWEAE1M") or []
        if isinstance(skills_raw, str):
            skills_raw = [skills_raw]
        # AT multipleSelects returns list of strings (option names)
        skills = [s if isinstance(s, str) else s.get("name", "") for s in skills_raw]

        # Ring linked records -> names via lookup
        ring_t0 = resolve_ring(f.get("fldSUhJQEB1gOBpZS", []), ring_lookup)
        ring_t1 = resolve_ring(f.get("fld2jAIh9BShadM13", []), ring_lookup)
        ring_t2 = resolve_ring(f.get("fld7y1eBeHlAxo60i", []), ring_lookup)

        # Ring cascade: current recommended ring = highest tier confirmed
        # T2 > T1 > T0 -- used as the single `ring` field in HERO_META
        ring_current = ring_t2 or ring_t1 or ring_t0

        hero = {
            "name":        f.get("fldjwHFmQKzKu1s4v", ""),
            "type":        hero_type,
            "rarity":      rarity,
            "season":      f.get("fld1lrjDbLkS09FZW", ""),
            "role":        f.get("fld43lU9NUaf9sGXP", ""),
            "skill1":      f.get("fldNXxq2FgIGJVIxT", "") or "",
            "skill2":      f.get("fldTGfvzcln4lowxl", "") or "",
            "skill3_rec":  f.get("fldZxFZW6h7Efux6b", "") or "",
            "skill4_rec":  f.get("fldRkDxVWSX5iDZ0J", "") or "",
            "skills":      skills,
            "ring":        ring_current,
            "ring_t0":     ring_t0,
            "ring_t1":     ring_t1,
            "ring_t2":     ring_t2,
            "mount_temp":  mount_temp,
            "mount_trait": f.get("fldNkvsqF3GwvwIVo", "") or "",
            "mount_trait2":f.get("fldG6Jn32lZL0hofC", "") or "",
            "adornment":   adorn,
            "pairings":    f.get("fldwn0BheYYzLQgl2", "") or "",
            "data_status": status,
        }
        heroes.append(hero)

    # Sort: Legendary/Mythical first, then Epic; within each group alphabetically
    def sort_key(h):
        rarity_order = {"Mythical": 0, "Legendary": 1, "Epic": 2}
        return (rarity_order.get(h["rarity"], 9), h["name"])

    heroes.sort(key=sort_key)
    return heroes

# ── JS serialiser ─────────────────────────────────────────────────────────────
def js_str(v) -> str:
    """Escape a Python string for safe embedding in a JS string literal."""
    if isinstance(v, list):
        v = ", ".join(v)
    elif not isinstance(v, str):
        v = str(v)
    return v.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")

def hero_to_js(h: dict) -> str:
    skills_js = ",".join(f'"{js_str(s)}"' for s in h["skills"])
    return (
        f'  {{name:"{js_str(h["name"])}",type:"{js_str(h["type"])}",'
        f'rarity:"{js_str(h["rarity"])}",season:"{js_str(h["season"])}",'
        f'role:"{js_str(h["role"])}",skill1:"{js_str(h["skill1"])}",'
        f'skill2:"{js_str(h["skill2"])}",skills:[{skills_js}],'
        f'ring:"{js_str(h["ring"])}",ring_t0:"{js_str(h["ring_t0"])}",'
        f'ring_t1:"{js_str(h["ring_t1"])}",ring_t2:"{js_str(h["ring_t2"])}",'
        f'mount_temp:"{js_str(h["mount_temp"])}",mount_trait:"{js_str(h["mount_trait"])}",'
        f'mount_trait2:"{js_str(h["mount_trait2"])}",'
        f'adornment:"{js_str(h["adornment"])}",'
        f'skill3_rec:"{js_str(h["skill3_rec"])}",skill4_rec:"{js_str(h["skill4_rec"])}"'
        f'}}'
    )

def build_hero_meta_js(heroes: list[dict]) -> str:
    lines = [f"// ── HERO META — generated from Airtable {BASE_ID} | {len(heroes)} heroes ─────"]
    lines.append("// DO NOT EDIT THIS BLOCK MANUALLY.")
    lines.append("// Run generate_hero_meta.py to regenerate from Airtable.")
    lines.append(f"const HERO_META = [")
    lines.append(",\n".join(hero_to_js(h) for h in heroes))
    lines.append("];")
    return "\n".join(lines)

def ring_pool_entry_to_js(r: dict) -> str:
    roles_js = ",".join(f'"{js_str(s)}"' for s in r["suits_roles"])
    troops_js = ",".join(f'"{js_str(s)}"' for s in r["suits_troops"])
    meta_override_js = "true" if r["meta_override"] else "false"
    return (
        f'  {{name:"{js_str(r["name"])}",tier:"{js_str(r["tier"])}",'
        f'suits_roles:[{roles_js}],'
        f'suits_troops:[{troops_js}],priority_rank:"{js_str(r["priority_rank"])}",'
        f'wrong_for:"{js_str(r["wrong_for"])}",ftp_rating:"{js_str(r["ftp_rating"])}",'
        f'meta_override:{meta_override_js}}}'
    )

def build_ring_pool_js(pool: list[dict]) -> str:
    lines = [f"// ── RING POOL — generated from Airtable {BASE_ID} | {len(pool)} rings ─────"]
    lines.append("// DO NOT EDIT THIS BLOCK MANUALLY.")
    lines.append("// Run generate_hero_meta.py to regenerate from Airtable.")
    lines.append("// Suitability data only -- cascade allocation logic runs at query")
    lines.append("// time in app.py, not baked into hero records here.")
    lines.append("const RING_POOL = [")
    lines.append(",\n".join(ring_pool_entry_to_js(r) for r in pool))
    lines.append("];")
    return "\n".join(lines)

# ── Widget patcher ────────────────────────────────────────────────────────────
# Matches the existing HERO_META block including the comment header lines
HERO_META_RE = re.compile(
    r"// ── HERO META.*?^const HERO_META = \[.*?^\];",
    re.DOTALL | re.MULTILINE,
)

# Matches an existing RING_POOL block including its comment header lines
RING_POOL_RE = re.compile(
    r"// ── RING POOL.*?^const RING_POOL = \[.*?^\];",
    re.DOTALL | re.MULTILINE,
)

# Anchor used to insert RING_POOL on the first run, when no block exists yet.
# Placed right after HERO_BY_NAME is built, before the season-filter section.
HERO_BY_NAME_ANCHOR = re.compile(
    r"(const HERO_BY_NAME = \{\};\nHERO_META\.forEach\(h => \{ HERO_BY_NAME\[h\.name\] = h; \}\);\n)",
)

def patch_widget(html: str, hero_js: str, ring_js: str) -> str:
    if not HERO_META_RE.search(html):
        raise ValueError(
            "Could not find HERO_META block in widget HTML. "
            "Expected pattern: '// ── HERO META' comment followed by 'const HERO_META = ['."
        )
    html = HERO_META_RE.sub(hero_js, html, count=1)

    if RING_POOL_RE.search(html):
        html = RING_POOL_RE.sub(ring_js, html, count=1)
    elif HERO_BY_NAME_ANCHOR.search(html):
        html = HERO_BY_NAME_ANCHOR.sub(lambda m: m.group(1) + "\n" + ring_js + "\n", html, count=1)
    else:
        raise ValueError(
            "Could not find a RING_POOL block or the HERO_BY_NAME anchor to "
            "insert one. Inspect the widget structure manually."
        )
    return html

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    ring_records = fetch_rings()
    ring_lookup  = build_ring_lookup(ring_records)
    ring_pool    = build_ring_pool(ring_records)
    heroes       = fetch_heroes(ring_lookup)
    hero_js      = build_hero_meta_js(heroes)
    ring_js      = build_ring_pool_js(ring_pool)

    print(f"\nGenerated HERO_META: {len(heroes)} heroes", file=sys.stderr)
    print(f"Generated RING_POOL: {len(ring_pool)} rings", file=sys.stderr)

    if DRY_RUN:
        print(hero_js)
        print(ring_js)
        return

    html = output_path.read_text(encoding="utf-8")
    patched = patch_widget(html, hero_js, ring_js)
    output_path.write_text(patched, encoding="utf-8")
    print(f"Written to {output_path}", file=sys.stderr)
    print("Done. Commit and push via Claude Code.", file=sys.stderr)

if __name__ == "__main__":
    main()
