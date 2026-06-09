# AIGA System — Operations Reference
## knowledge/system/system_ops.md
**Version:** 1.0 | **Date:** June 2026
**Audience:** AIGA product team (Network Grey) — not bot-facing
**Purpose:** Deployment rules, bot architecture, KB management, data discipline

---

## KB ARCHITECTURE

### Folder Structure

```
knowledge/
├── AIGA_Knowledge_Base_Index.md     ← Master index and routing brain
├── heroes/
│   ├── profiles/
│   │   ├── season_1.md through season_6.md
│   ├── tiers/
│   │   └── hero_tiers.md
│   └── mounts/
│       └── (from AIGA_Mount_System_Reference.md)
├── gear/
│   ├── equipment/
│   │   └── gear_equipment.md
│   └── rings/
│       └── gear_rings.md
├── marches/
│   └── (march composition files)
├── combat/
│   ├── combat_mechanics.md
│   └── combat_civilizations.md
├── events/
│   ├── events_mge.md
│   ├── events_mee.md
│   └── events_all.md
├── base/
│   ├── base_buildings.md
│   └── base_troops_healing.md
├── economy/
│   ├── economy_gathering_coins.md
│   └── economy_vip.md
└── system/
    └── system_ops.md (this file)
```

### Bot.py — Critical Requirement

Bot uses `rglob` (not `glob`) to scan subfolders. If `glob` is used, none of the subfolder KB files are loaded.

```python
# CORRECT
knowledge_dir.rglob("*.md")

# WRONG — misses all subfolders
knowledge_dir.glob("*.md")
```

### KEYWORD_MAP (bot.py routing)

The KEYWORD_MAP injects the top 2-3 matching documents per query. All paths must match the index exactly. Any file path change in the KB requires simultaneous update in KEYWORD_MAP.

**Rule:** Never add a file to the repository without a corresponding index entry. Never update a path on GitHub without updating KEYWORD_MAP in bot.py simultaneously.

---

## DEPLOYMENT

### Infrastructure
- **Hosting:** Railway.app
- **Repository:** GitHub (main branch only — Railway deploys from main)
- **Bot version:** v7 stable | v8 rolled back (Discord private thread permission issue)
- **Models:** Haiku (free Discord tier) | Sonnet (Commander tier web app)

### GitHub Rules
- Does not extract zip files on upload
- Automatically deletes empty folders
- Browser editor unreliable for large files — use Upload Files instead
- Always deploy from main branch

### Railway
- All environment variables set in Railway dashboard
- Redeploy triggers on push to main
- Monitor logs for errors immediately after deploy

---

## DATA DISCIPLINE

### Source Hierarchy (trust order)

| Priority | Source | Trust level |
|---|---|---|
| 1 | aoem-calculator (MIT, Codeberg, juan_jm) | Highest — open source, verifiable |
| 2 | Official AoEM YouTube / aoemobile.com | High — developer content |
| 3 | Official AoEM Dev Columns | High — developer content |
| 4 | Theria Games (theriagames.com) | Medium-high — detailed, generally accurate |
| 5 | aoemobileguides.com | Medium — community, disclaim accuracy |
| 6 | Van (YouTube) | Medium — community, credit by name |
| 7 | Fandom Wiki | Low-medium — frequently outdated |
| 8 | General community / unattributed | Low — flag as unverified |

### Flagging Conventions
- `*[verify in-game]*` — data needs in-game confirmation before advising
- `*[community knowledge]*` — not from primary source, may be inaccurate
- `*[potential info gap]*` — data conflict flagged, not resolved
- `[estimated]` — calculated/extrapolated, not directly sourced

### KB Management Rules
- Flag data conflicts rather than resolving by assumption
- Never delete index entries — only increment version on edits
- Silent background updates preferred over full file output (brief confirmation only)
- Fact, hypothesis, and opinion must be clearly distinguished in all KB files

---

## KNOWN VERIFIED RULES (NEVER OVERRIDE)

Critical data points confirmed in-game or from primary sources:

| Rule | Status |
|---|---|
| Train highest available tier directly — promotions earn zero MGE/MEE points | Verified |
| Never spend SP on commander auto-skills (they level with XP) | Verified |
| Skill slot level transfers carry existing level to replacement; star ratings lost | Verified |
| Rings return to inventory when replaced (not destroyed) | Verified |
| Power score = vanity metric, not combat performance indicator | Verified |
| Peace shield cooldown: 15 minutes after all battle actions halt | Verified |
| Ring of Daisy BIS for Lu Bu — confirmed 40+ battle reports | Verified |
| Tribal rallies do not award hero XP | Verified in-game |
| Forge kit cost lv20→30: ~2,340-2,548 kits | Verified in-game |
| Henry IV correct skills: Ultimate Strategy + Strategy Master's Gift | Verified |
| Josephine correct skills: Weak Spot Attack + Double Attack | Verified |
| Cyrus the Great is Pikemen (source lists him as Cavalry/Archer — source error) | Verified |
| Otto I is dual Cavalry/Pikemen | Verified |
| Epic × Epic mount breeding = Epic only (not Legendary) | Verified |
| Legendary × Legendary breeding required for Celestial Charger | Verified |

---

## KNOWN GAPS — PRIORITY ORDER

### Critical
- Lu Bu hero guide — NOT in Drive (highest priority KB gap)
- Arabs civilization full stat bonuses — 9th civ confirmed, not documented
- Hero sub-rank medal costs — 5 sub-ranks per rank confirmed, costs unknown
- TiMi/Level Infinite explicit fan content policy — not yet located

### High Priority
- Lagertha, Elizabeth I, Leonidas I, Charlemagne, Mehmed II, Saladin, Boudica — Drive sources not in collection
- T5 MEE pts conflict: multiplier implies 200, troop table shows 160 — verify in-game
- Primordial Conflict event — not in AIGA KB
- Japanese civilization full passive bonus list (Gus plays Japanese)

### Medium Priority
- Advent wheel pack size (5 spins vs 10 spins for 4,200 EC) — verify before advising
- Smithy building upgrade costs — not in aoem-calculator source
- University military tree node unlock levels — incomplete
- Otto I season placement — listed as S5, confirm in-game

### Low Priority (Known data issues — do not use without flagging)
- Fandom wiki Cyrus entry (unit type error)
- Fandom wiki Julius Caesar civ entry (suspected error)
- Ring of Mamba / Ring of Seahorse duplicate skill description

---

## LEGAL COMPLIANCE

AIGA operates in full compliance with AoEM developer terms. All content is transformative commentary and strategic advisory — not reproduction of copyrighted game content.

**Required disclaimer on all player-facing outputs:**
"AIGA is a product of Network Grey. Powered by Anthropic Claude. Not affiliated with TiMi Studio Group or Level Infinite. All game content, hero names, mechanics and imagery are the intellectual property of their respective owners."

**Minimum age:** AoEM EULA requires 18+ (or minimum legal age in jurisdiction). AIGA should not provide account-level advice to users who indicate they are under 18.

**Calculator data:** aoem-calculator (MIT licence, Codeberg, juan_jm/aoem-calculator). Development stopped October 2025. All numerical data from this source is reliable up to October 2025 — flag post-October changes as *[verify in-game]*.

---

## PRODUCT TIERS

| Tier | Platform | Model | Features |
|---|---|---|---|
| Free | Discord bot | Haiku | Stateless, keyword-based context injection, general AoEM advice |
| Commander | Web app (Flask/Railway) | Sonnet | Deeper analysis, War Chest file upload, account-specific recommendations |
| War Advisor | Web app (future) | Sonnet | Alliance leadership tools, rally coordination, MEE/KvK strategy |

**Player data:** AIGA Workbook (Google Sheets/Excel, uploaded per session as authoritative profile). Player profiles being migrated from window.localStorage → Flask endpoints backed by Airtable.

---

*AIGA is a product of Network Grey. Powered by Anthropic Claude. Not affiliated with TiMi Studio Group or Level Infinite.*
