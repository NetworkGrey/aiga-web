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
  FTP Rating       fldk2wY18WiRRsFAn  singleSelect
  Meta Override    fldbXiKwsrqyqCDp1  checkbox
  Meta Status      fldKKhAmGwm5yRG6u  singleSelect
  Data Status      fldYff3M7BIPSe7nQ  singleSelect
  Excluded Roles   fldOfSZBqQ1vNJa0c  multipleSelects  } Excluded For (functional):
  Excluded Troops  fldAkUVuRKg0U0TI8  multipleSelects  } drives RED
  Excluded Kits    fldjzHpeHCrJ4FFgH  multipleSelects  }
  Reserved Claimants fld4BaayZ2QXLV8P4 links -> Heroes   Reserved For (allocation): ORANGE + move

  Excluded and Reserved are two different fields with two different marks
  (Diff Rules Spec v1.0). Export both; never collapse them into one. The
  prose Excluded For / Reserved For fields are notes and are not exported.

Adornment Effects table (tblHemWBNGb45t6E6):
  Special Effect   fldiXIOnbWVJIxOIy  singleLineText
  Troop Type       fldNK8dMlbHxH6wHG  singleSelect
  Data Status      fldt6RcdtkRS1V8KW  singleSelect
  Excluded Roles   fldGGJYIGzlIWnm2O  multipleSelects
  Excluded Troops  fldpV6vE3u4lguSU0  multipleSelects
  Excluded Kits    fldMkkNTZOrhl5lSz  multipleSelects
  Reserved Claimants fldTiH0zDRfkIVxio links -> Heroes

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
ADORNMENT_EFFECTS_TABLE = "tblHemWBNGb45t6E6"
MOUNT_TRAITS_TABLE      = "tblcgBlXf7Pu10N7G"
GEM_TYPES_TABLE         = "tblVfHxuJj77b8nOi"
GEAR_PIECES_TABLE       = "tblLuhHyJAQ2uCEQV"

# Heroes-table link fields holding each gear slot's meta gem type. Legs takes
# one gem of each category, so it has three fields.
META_GEM_FIELDS = {
    "head":          "fldKL0lPSX6Gye0Pc",
    "arms":          "fld999y771ID6joTe",
    "chest":         "fldIj9AEDHE2sbc1d",
    "legs_strategy": "fldFEPo2hJMBRU1De",
    "legs_hero":     "fldrEuF6qF2OCZ6Gf",
    "legs_tactic":   "fld4Xhxg3KPK54jCv",
}

# Mount trait pool -> the mount attribute a damage-percentage trait scales off.
POOL_ATTRIBUTE = {"Might Damage": "Might", "Strategy Damage": "Strategy"}

# Placeholder option Airtable shows in an empty Skill Alternates select.
SKILL_ALTERNATES_PLACEHOLDER = "(populate from Skill Pool as confirmed)"
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

# The hero card page reads the same generated blocks from its own data file.
CARD_DATA_PATH = Path(__file__).resolve().parent / "hero_card" / "card_data.js"

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

def linked_names(raw, id_to_name: dict[str, str]) -> list[str]:
    """Normalizes a multipleRecordLinks value (record IDs, or {id, name}
    objects) to linked record names, preserving link order."""
    names = []
    for link in raw or []:
        if isinstance(link, dict):
            name = link.get("name") or id_to_name.get(link.get("id", ""), "")
        else:
            name = id_to_name.get(link, "")
        if name:
            names.append(name)
    return names

def hero_name_lookup(hero_records: list[dict]) -> dict[str, str]:
    """Returns {record_id: hero_name} for resolving Reserved Claimants links."""
    return {
        rec["id"]: rec.get("fields", {}).get("fldjwHFmQKzKu1s4v", "")
        for rec in hero_records
        if rec.get("fields", {}).get("fldjwHFmQKzKu1s4v")
    }

# ── Build ring pool: suitability data for the pool-based allocation model ─────
def build_ring_pool(ring_records: list[dict], hero_names: dict[str, str]) -> list[dict]:
    """Returns every ring's suitability and diff-rule data. The cascade
    allocation and the card marks are both derived elsewhere at query time;
    this only exports the pool's raw reference data."""
    pool = []
    for rec in ring_records:
        f = rec.get("fields", {})
        name = f.get("fldIi2LvUz6PybBtF", "") or ""
        if not name.strip():
            continue
        pool.append({
            "name":               name,
            "tier":               select_name(f.get("fldwHCQkDc4pDMa4l")),
            "suits_roles":        multiselect_names(f.get("fldNpjqtn6OGX8wGS")),
            "suits_troops":       multiselect_names(f.get("fldQem8XyrW9pgenW")),
            "priority_rank":      f.get("fldsEISuRO7CDGwkv", "") or "",
            "ftp_rating":         select_name(f.get("fldk2wY18WiRRsFAn")),
            "meta_override":      bool(f.get("fldbXiKwsrqyqCDp1", False)),
            "meta_status":        select_name(f.get("fldKKhAmGwm5yRG6u")),
            "data_status":        select_name(f.get("fldYff3M7BIPSe7nQ")),
            "excluded_roles":     multiselect_names(f.get("fldOfSZBqQ1vNJa0c")),
            "excluded_troops":    multiselect_names(f.get("fldAkUVuRKg0U0TI8")),
            "excluded_kits":      multiselect_names(f.get("fldjzHpeHCrJ4FFgH")),
            "reserved_claimants": linked_names(f.get("fld4BaayZ2QXLV8P4"), hero_names),
        })
    print(f"  {len(pool)} rings in pool.", file=sys.stderr)
    return pool

# ── Build adornment effect pool ────────────────────────────────────────────────
def build_adornment_effects(effect_records: list[dict], hero_names: dict[str, str]) -> list[dict]:
    """Returns every adornment special effect with its troop pool and
    diff-rule data. Universal effects appear in every troop type's pool."""
    effects = []
    for rec in effect_records:
        f = rec.get("fields", {})
        name = f.get("fldiXIOnbWVJIxOIy", "") or ""
        if not name.strip():
            continue
        effects.append({
            "name":               name,
            "troop_type":         select_name(f.get("fldNK8dMlbHxH6wHG")),
            "data_status":        select_name(f.get("fldt6RcdtkRS1V8KW")),
            "excluded_roles":     multiselect_names(f.get("fldGGJYIGzlIWnm2O")),
            "excluded_troops":    multiselect_names(f.get("fldpV6vE3u4lguSU0")),
            "excluded_kits":      multiselect_names(f.get("fldMkkNTZOrhl5lSz")),
            "reserved_claimants": linked_names(f.get("fldTiH0zDRfkIVxio"), hero_names),
        })
    effects.sort(key=lambda e: (e["troop_type"] != "Universal", e["troop_type"], e["name"]))
    print(f"  {len(effects)} adornment effects.", file=sys.stderr)
    return effects

# ── Fetch heroes ──────────────────────────────────────────────────────────────
def fetch_hero_records() -> list[dict]:
    print("Fetching Heroes table...", file=sys.stderr)
    records = fetch_all(HEROES_TABLE)
    print(f"  {len(records)} hero records fetched.", file=sys.stderr)
    return records

def record_names(records: list[dict], name_field: str) -> dict[str, str]:
    """Returns {record_id: name} for resolving links into a table."""
    return {
        rec["id"]: rec.get("fields", {}).get(name_field, "")
        for rec in records
        if rec.get("fields", {}).get(name_field)
    }

def build_heroes(records: list[dict], names: dict[str, dict[str, str]]) -> list[dict]:
    """names holds {record_id: name} lookups for "rings", "traits",
    "effects" and "gems", used to resolve the hero's linked meta records."""
    heroes = []
    for rec in records:
        f = rec.get("fields", {})

        # Skip junk rows: blank records, or template/header rows where the
        # Name field literally contains the field's own label ("Name").
        name_val = f.get("fldjwHFmQKzKu1s4v", "") or ""
        if not name_val.strip() or name_val.strip() == "Name":
            continue

        # Type: multipleSelects of combined options, e.g. ["CAV/ARC"] -> "CAV/ARC"
        hero_type = "/".join(multiselect_names(f.get("fld39hloCOq4Kw507")))

        # Skill Pool: use `or []`, not a .get() default. .get(key, []) only
        # falls back when the key is missing, not when Airtable returns it
        # present but falsy, which silently emptied skills[] before.
        skills = multiselect_names(f.get("fldIINIVqQWWEAE1M") or [])

        # Ring linked records -> names
        ring_t0 = (linked_names(f.get("fldSUhJQEB1gOBpZS"), names["rings"]) or [""])[0]
        ring_t1 = (linked_names(f.get("fld2jAIh9BShadM13"), names["rings"]) or [""])[0]
        ring_t2 = (linked_names(f.get("fld7y1eBeHlAxo60i"), names["rings"]) or [""])[0]

        # Ring cascade: current recommended ring = highest tier confirmed
        # T2 > T1 > T0 -- used as the single `ring` field in HERO_META
        ring_current = ring_t2 or ring_t1 or ring_t0

        skill4_recs = multiselect_names(f.get("fldRkDxVWSX5iDZ0J"))
        alternates = lambda field: [
            s for s in multiselect_names(f.get(field)) if s != SKILL_ALTERNATES_PLACEHOLDER
        ]

        hero = {
            "name":        name_val,
            "type":        hero_type,
            "rarity":      select_name(f.get("fldAAEYZ023m1wApS")),
            "season":      f.get("fld1lrjDbLkS09FZW", "") or "",
            "role":        f.get("fld43lU9NUaf9sGXP", "") or "",
            "skill1":      f.get("fldNXxq2FgIGJVIxT", "") or "",
            "skill2":      f.get("fldTGfvzcln4lowxl", "") or "",
            "skill3_rec":  select_name(f.get("fldZxFZW6h7Efux6b")),
            "skill4_rec":  ", ".join(skill4_recs),
            "skills":      skills,
            "ring":        ring_current,
            "ring_t0":     ring_t0,
            "ring_t1":     ring_t1,
            "ring_t2":     ring_t2,
            "mount_temp":  select_name(f.get("fld5mpoP8CPc9rHmO")),
            "mount_trait": select_name(f.get("fldNkvsqF3GwvwIVo")),
            "mount_trait2":select_name(f.get("fldG6Jn32lZL0hofC")),
            "adornment":   select_name(f.get("fldRRvKyctnaWK890")),
            "pairings":    f.get("fldwn0BheYYzLQgl2", "") or "",
            "data_status": select_name(f.get("fldICAkHKI5NFroeh")),
            # Hero card diff-rule inputs (Diff Rules Spec v1.0)
            "card_role":         select_name(f.get("fldHxHxpxdSRkcHN3")),
            "damage_kit":        select_name(f.get("fldJ9LyJlg5n7A9oM")),
            "mount_traits":      linked_names(f.get("fldWob9aMkmGUN3aQ"), names["traits"]),
            "mount_attributes":  multiselect_names(f.get("fldohoG1KkcE93Lar")),
            "adornment_effects": linked_names(f.get("fldTQgOFsVORsvhz9"), names["effects"]),
            "meta_gems": {
                slot: (linked_names(f.get(field), names["gems"]) or [""])[0]
                for slot, field in META_GEM_FIELDS.items()
            },
            "skill4_recs":       skill4_recs,
            "skill3_alternates": alternates("fldstCJSDPkYWCy6V"),
            "skill4_alternates": alternates("fld0b4RehvTVVYBeA"),
        }
        heroes.append(hero)

    # Sort: Legendary/Mythical first, then Epic; within each group alphabetically
    def sort_key(h):
        rarity_order = {"Mythical": 0, "Legendary": 1, "Epic": 2}
        return (rarity_order.get(h["rarity"], 9), h["name"])

    heroes.sort(key=sort_key)
    return heroes

# ── Build card reference tables ────────────────────────────────────────────────
def build_mount_traits(records: list[dict], hero_names: dict[str, str]) -> list[dict]:
    traits = []
    for rec in records:
        f = rec.get("fields", {})
        name = f.get("fldpO8Y8NOKBb7HHV", "") or ""
        if not name.strip():
            continue
        pool = select_name(f.get("flduHHddFcUVT1cHy"))
        traits.append({
            "name":                     name,
            "pool":                     pool,
            "attribute":                POOL_ATTRIBUTE.get(pool, ""),
            "requires_attribute_match": bool(f.get("fldU0MW7rWmPkaif7", False)),
            "meta_status":              select_name(f.get("fldlrvFC7GQxEz7VO")),
            "data_status":              select_name(f.get("fldxzx6Xbbf2tS0Jy")),
            "excluded_roles":           multiselect_names(f.get("fldKmE7FioVcHEAul")),
            "excluded_troops":          multiselect_names(f.get("fldDOiZy8c8mjhYTx")),
            "excluded_kits":            multiselect_names(f.get("fldp4udI7pVzZJWgL")),
            "reserved_claimants":       linked_names(f.get("fldo4wLRyCZifw5p7"), hero_names),
        })
    traits.sort(key=lambda t: t["name"])
    print(f"  {len(traits)} mount traits.", file=sys.stderr)
    return traits

def build_gem_types(records: list[dict]) -> list[dict]:
    gem_names = record_names(records, "fldoJJzLugm0dNNxn")
    gems = []
    for rec in records:
        f = rec.get("fields", {})
        name = f.get("fldoJJzLugm0dNNxn", "") or ""
        if not name.strip():
            continue
        gems.append({
            "name":            name,
            "category":        select_name(f.get("fldVkM5GOHGQEEQcT")),
            "is_placeholder":  bool(f.get("fldn4917mIUHZ6NKi", False)),
            "placeholder_for": linked_names(f.get("fldt5HBzTgLQcOKJg"), gem_names),
            "data_status":     select_name(f.get("fldmBi9nBn58oX2L7")),
        })
    gems.sort(key=lambda g: (g["category"], g["name"]))
    print(f"  {len(gems)} gem types.", file=sys.stderr)
    return gems

def build_gear_pieces(records: list[dict]) -> list[dict]:
    rarity_order = {"Legendary": 0, "Epic": 1, "Rare": 2}
    slot_order = {"Head": 0, "Arms": 1, "Chest": 2, "Legs": 3}
    pieces = []
    for rec in records:
        f = rec.get("fields", {})
        name = f.get("fldJylmVAXXOWXJyS", "") or ""
        if not name.strip():
            continue
        pieces.append({
            "name":        name,
            "troop_type":  select_name(f.get("fldODJy5jeE9B9dpd")),
            "slot":        select_name(f.get("fldtnTdOGDwGSekMx")),
            "rarity":      select_name(f.get("fldW2cD70FGBWAGmR")),
            "max_level":   f.get("fldqW6JrsaOy7z2yr") or 0,
            "data_status": select_name(f.get("fldoYsAOVAjyErZBM")),
        })
    pieces.sort(key=lambda p: (p["troop_type"], slot_order.get(p["slot"], 9), rarity_order.get(p["rarity"], 9)))
    print(f"  {len(pieces)} gear pieces.", file=sys.stderr)
    return pieces

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
    meta_gems_js = "{" + ",".join(f'{slot}:"{js_str(gem)}"' for slot, gem in h["meta_gems"].items()) + "}"
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
        f'skill3_rec:"{js_str(h["skill3_rec"])}",skill4_rec:"{js_str(h["skill4_rec"])}",'
        f'card_role:"{js_str(h["card_role"])}",damage_kit:"{js_str(h["damage_kit"])}",'
        f'mount_traits:{js_list(h["mount_traits"])},mount_attributes:{js_list(h["mount_attributes"])},'
        f'adornment_effects:{js_list(h["adornment_effects"])},'
        f'meta_gems:{meta_gems_js},'
        f'skill4_recs:{js_list(h["skill4_recs"])},'
        f'skill3_alternates:{js_list(h["skill3_alternates"])},skill4_alternates:{js_list(h["skill4_alternates"])}'
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

def js_list(values: list[str]) -> str:
    return "[" + ",".join(f'"{js_str(v)}"' for v in values) + "]"

def ring_pool_entry_to_js(r: dict) -> str:
    meta_override_js = "true" if r["meta_override"] else "false"
    return (
        f'  {{name:"{js_str(r["name"])}",tier:"{js_str(r["tier"])}",'
        f'suits_roles:{js_list(r["suits_roles"])},suits_troops:{js_list(r["suits_troops"])},'
        f'priority_rank:"{js_str(r["priority_rank"])}",ftp_rating:"{js_str(r["ftp_rating"])}",'
        f'meta_override:{meta_override_js},meta_status:"{js_str(r["meta_status"])}",'
        f'data_status:"{js_str(r["data_status"])}",'
        f'excluded_roles:{js_list(r["excluded_roles"])},excluded_troops:{js_list(r["excluded_troops"])},'
        f'excluded_kits:{js_list(r["excluded_kits"])},reserved_claimants:{js_list(r["reserved_claimants"])}}}'
    )

def adornment_effect_to_js(e: dict) -> str:
    return (
        f'  {{name:"{js_str(e["name"])}",troop_type:"{js_str(e["troop_type"])}",'
        f'data_status:"{js_str(e["data_status"])}",'
        f'excluded_roles:{js_list(e["excluded_roles"])},excluded_troops:{js_list(e["excluded_troops"])},'
        f'excluded_kits:{js_list(e["excluded_kits"])},reserved_claimants:{js_list(e["reserved_claimants"])}}}'
    )

def mount_trait_to_js(t: dict) -> str:
    requires = "true" if t["requires_attribute_match"] else "false"
    return (
        f'  {{name:"{js_str(t["name"])}",pool:"{js_str(t["pool"])}",attribute:"{js_str(t["attribute"])}",'
        f'requires_attribute_match:{requires},meta_status:"{js_str(t["meta_status"])}",'
        f'data_status:"{js_str(t["data_status"])}",'
        f'excluded_roles:{js_list(t["excluded_roles"])},excluded_troops:{js_list(t["excluded_troops"])},'
        f'excluded_kits:{js_list(t["excluded_kits"])},reserved_claimants:{js_list(t["reserved_claimants"])}}}'
    )

def gem_type_to_js(g: dict) -> str:
    placeholder = "true" if g["is_placeholder"] else "false"
    return (
        f'  {{name:"{js_str(g["name"])}",category:"{js_str(g["category"])}",is_placeholder:{placeholder},'
        f'placeholder_for:{js_list(g["placeholder_for"])},data_status:"{js_str(g["data_status"])}"}}'
    )

def gear_piece_to_js(p: dict) -> str:
    return (
        f'  {{name:"{js_str(p["name"])}",troop_type:"{js_str(p["troop_type"])}",slot:"{js_str(p["slot"])}",'
        f'rarity:"{js_str(p["rarity"])}",max_level:{int(p["max_level"])},data_status:"{js_str(p["data_status"])}"}}'
    )

def build_block_js(label: str, const: str, entries: list[str], notes: list[str]) -> str:
    lines = [f"// ── {label} — generated from Airtable {BASE_ID} | {len(entries)} entries ─────"]
    lines.append("// DO NOT EDIT THIS BLOCK MANUALLY.")
    lines.append("// Run generate_hero_meta.py to regenerate from Airtable.")
    lines.extend(f"// {n}" for n in notes)
    lines.append(f"const {const} = [")
    lines.append(",\n".join(entries))
    lines.append("];")
    return "\n".join(lines)

def build_ring_pool_js(pool: list[dict]) -> str:
    return build_block_js("RING POOL", "RING_POOL", [ring_pool_entry_to_js(r) for r in pool], [
        "Reference data only -- cascade allocation and card marks are derived",
        "at query time, never baked into hero records here.",
    ])

def build_adornment_effects_js(effects: list[dict]) -> str:
    return build_block_js("ADORNMENT EFFECTS", "ADORNMENT_EFFECTS", [adornment_effect_to_js(e) for e in effects], [
        "Special effects per troop pool; Universal effects apply to every troop type.",
    ])

def build_mount_traits_js(traits: list[dict]) -> str:
    return build_block_js("MOUNT TRAITS", "MOUNT_TRAITS", [mount_trait_to_js(t) for t in traits], [
        "Temperament is deliberately absent: it never drives a mark (Mount KB v7 Rule 2).",
    ])

def build_gem_types_js(gems: list[dict]) -> str:
    return build_block_js("GEM TYPES", "GEM_TYPES", [gem_type_to_js(g) for g in gems], [
        "Head takes Strategy, Arms takes Hero, Chest takes Tactic, Legs one of each.",
    ])

def build_gear_pieces_js(pieces: list[dict]) -> str:
    return build_block_js("GEAR PIECES", "GEAR_PIECES", [gear_piece_to_js(p) for p in pieces], [
        "Meta rarity is Legendary; a lower rarity of the right troop's set is an upgrade path.",
    ])

def build_card_data_js(blocks: list[str]) -> str:
    """The hero card page's data file: the same generated blocks as the
    widget, so both always come from one Airtable pull."""
    header = [
        "// AIGA hero card data -- generated by generate_hero_meta.py.",
        "// DO NOT EDIT MANUALLY. Run generate_hero_meta.py to regenerate from Airtable.",
        "",
    ]
    return "\n".join(header) + "\n\n".join(blocks) + "\n"

# ── Widget patcher ────────────────────────────────────────────────────────────
def block_re(label: str, const: str) -> re.Pattern:
    """Matches a generated block including its comment header lines."""
    return re.compile(rf"// ── {label}.*?^const {const} = \[.*?^\];", re.DOTALL | re.MULTILINE)

HERO_META_RE         = block_re("HERO META", "HERO_META")
RING_POOL_RE         = block_re("RING POOL", "RING_POOL")
ADORNMENT_EFFECTS_RE = block_re("ADORNMENT EFFECTS", "ADORNMENT_EFFECTS")
MOUNT_TRAITS_RE      = block_re("MOUNT TRAITS", "MOUNT_TRAITS")
GEM_TYPES_RE         = block_re("GEM TYPES", "GEM_TYPES")
GEAR_PIECES_RE       = block_re("GEAR PIECES", "GEAR_PIECES")

# Anchor used to insert RING_POOL on the first run, when no block exists yet.
# Placed right after HERO_BY_NAME is built, before the season-filter section.
HERO_BY_NAME_ANCHOR = re.compile(
    r"(const HERO_BY_NAME = \{\};\nHERO_META\.forEach\(h => \{ HERO_BY_NAME\[h\.name\] = h; \}\);\n)",
)

def replace_or_insert(html: str, pattern: re.Pattern, js: str, anchor: re.Pattern, name: str) -> str:
    """Replaces an existing generated block in place, or inserts it after
    the anchor on the first run."""
    if pattern.search(html):
        return pattern.sub(lambda _: js, html, count=1)
    if anchor.search(html):
        return anchor.sub(lambda m: m.group(0) + "\n" + js + "\n", html, count=1)
    raise ValueError(f"Could not find a {name} block or its insertion anchor. Inspect the widget structure manually.")

def patch_widget(html: str, hero_js: str, ring_js: str, adornment_js: str,
                 trait_js: str, gem_js: str, gear_js: str) -> str:
    if not HERO_META_RE.search(html):
        raise ValueError(
            "Could not find HERO_META block in widget HTML. "
            "Expected pattern: '// ── HERO META' comment followed by 'const HERO_META = ['."
        )
    html = HERO_META_RE.sub(lambda _: hero_js, html, count=1)
    html = replace_or_insert(html, RING_POOL_RE, ring_js, HERO_BY_NAME_ANCHOR, "RING_POOL")
    html = replace_or_insert(html, ADORNMENT_EFFECTS_RE, adornment_js, RING_POOL_RE, "ADORNMENT_EFFECTS")
    html = replace_or_insert(html, MOUNT_TRAITS_RE, trait_js, ADORNMENT_EFFECTS_RE, "MOUNT_TRAITS")
    html = replace_or_insert(html, GEM_TYPES_RE, gem_js, MOUNT_TRAITS_RE, "GEM_TYPES")
    html = replace_or_insert(html, GEAR_PIECES_RE, gear_js, GEM_TYPES_RE, "GEAR_PIECES")
    return html

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    hero_records   = fetch_hero_records()
    hero_names     = hero_name_lookup(hero_records)
    ring_records   = fetch_rings()
    print("Fetching Adornment Effects, Mount Traits, Gem Types, Gear Pieces...", file=sys.stderr)
    effect_records = fetch_all(ADORNMENT_EFFECTS_TABLE)
    trait_records  = fetch_all(MOUNT_TRAITS_TABLE)
    gem_records    = fetch_all(GEM_TYPES_TABLE)
    gear_records   = fetch_all(GEAR_PIECES_TABLE)

    names = {
        "rings":   build_ring_lookup(ring_records),
        "traits":  record_names(trait_records, "fldpO8Y8NOKBb7HHV"),
        "effects": record_names(effect_records, "fldiXIOnbWVJIxOIy"),
        "gems":    record_names(gem_records, "fldoJJzLugm0dNNxn"),
    }
    heroes     = build_heroes(hero_records, names)
    ring_pool  = build_ring_pool(ring_records, hero_names)
    adornments = build_adornment_effects(effect_records, hero_names)
    traits     = build_mount_traits(trait_records, hero_names)
    gems       = build_gem_types(gem_records)
    gear       = build_gear_pieces(gear_records)

    blocks = [
        build_hero_meta_js(heroes), build_ring_pool_js(ring_pool),
        build_adornment_effects_js(adornments), build_mount_traits_js(traits),
        build_gem_types_js(gems), build_gear_pieces_js(gear),
    ]
    print(f"\nGenerated HERO_META: {len(heroes)} heroes, RING_POOL: {len(ring_pool)}, "
          f"ADORNMENT_EFFECTS: {len(adornments)}, MOUNT_TRAITS: {len(traits)}, "
          f"GEM_TYPES: {len(gems)}, GEAR_PIECES: {len(gear)}", file=sys.stderr)

    if DRY_RUN:
        print("\n\n".join(blocks))
        return

    html = output_path.read_text(encoding="utf-8")
    output_path.write_text(patch_widget(html, *blocks), encoding="utf-8")
    print(f"Written to {output_path}", file=sys.stderr)
    CARD_DATA_PATH.write_text(build_card_data_js(blocks), encoding="utf-8")
    print(f"Written to {CARD_DATA_PATH}", file=sys.stderr)
    print("Done. Commit and push via Claude Code.", file=sys.stderr)

if __name__ == "__main__":
    main()
