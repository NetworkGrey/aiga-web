# AIGA Gear Reference — Equipment
## knowledge/gear/equipment/gear_equipment.md
**Version:** 1.0 | **Date:** June 2026
**Source:** aoem-calculator GearData.ts/GemsData.ts (MIT licence, juan_jm/aoem-calculator, Codeberg) + in-game verification

---

## GEAR OVERVIEW

Each hero equips 4 gear slots: Head, Hands, Body, Legs. Three rarity tiers exist. Gear is troop-type specific — only equip matching troop type to the hero's formation.

---

## GEAR PIECE NAMES BY TROOP TYPE

| Slot | Rare | Epic | Legendary |
|---|---|---|---|
| **Swordsmen** | | | |
| Head | Linen Kerchief | Laurel Crown | Blazing Heart |
| Hands | Sennit Bracer | Star Handguards | Flowing Force |
| Body | Wornout Armor | Silver Chest Armor | Infinite Land |
| Legs | Wanderer's Boots | Shadow Light Boots | Shadowless Wind |
| **Pikemen** | | | |
| Head | Simple Straw Hat | Plume Hat | Power of Abyss |
| Hands | Linen Gloves | Legacy Arm Armor | Ring of Chaos |
| Body | Cotton Top | Silk Shirt | Master of Death |
| Legs | Handmade Boots | Leather Boots | Nightmare Boots |
| **Cavalry** | | | |
| Head | Woollen Hood | Lion Helmet | Divine Crown |
| Hands | Northland Gauntlets | White Wolf Bracers | Contract of Light |
| Body | Chamois Shirt | Bear Chest Armor | Omniscience |
| Legs | Furry Boots | Feathered Iron Boots | Dust-Free Boots |
| **Archer** | | | |
| Head | Buckskin Hat | Eagle Eye Forehead Protector | Fiery Sun |
| Hands | Hunter Gauntlets | Skyshatter Gauntlets | Embrace of Effulgence |
| Body | Grizzly Chest Armor | Falcon Armor | Eternal Flare |
| Legs | Hare Boots | Night Owl Boots | Dawnbreak Boots |

---

## CRAFTING COSTS

| Rarity | Iron Meteorite | Craft time | MGE Day II score |
|---|---|---|---|
| Rare | 150 | 2h | 1,000 pts |
| Epic | 400 | 6h | 5,000 pts |
| Legendary | 3,000 | ~40h (39h 59m) | 30,000 pts |

**Smithy speed reduction by level:**

| Smithy lv | Speed reduction |
|---|---|
| 15 | 36% |
| 20 | 56% |
| 25 | 78% |
| 30 | ~100% (halves effective time) |

**Rules:**
- Do not use speedups on Legendary crafting until Smithy lv15 minimum
- Smithy lv25 recommended for MGE Day II Legendary runs (~25-26h per piece)
- Smithy lv15 = minimum threshold for Legendary to be practical

---

## MAX LEVELS AND FORGE TOOL COSTS

| Rarity | Max level | Total forge tools to max |
|---|---|---|
| Rare | 40 | ~8,000 *[estimated]* |
| Epic | 60 | ~18,900 *[estimated]* |
| Legendary | 80 | ~32,400 *[estimated]* |

**Forge tool cost per level (selected milestones):**

| Level | Tools per level | Cumulative tools |
|---|---|---|
| 1 | 0 | 0 |
| 5 | 50 | 140 |
| 10 | 100 | 640 |
| 20 | 200 | 2,640 |
| 30 | 300 | 6,640 |
| 40 | 400 | 12,640 |
| 50 | 500 | 20,640 |
| 60 | 600 | 30,640 |
| 70 | 700 | 42,640 |
| 80 | 800 | 56,640 |

**Verified spend:** lv20→30 = ~2,340-2,548 tools (confirmed in-game).

---

## GEAR MILESTONE LEVELS

| Level | What changes |
|---|---|
| 10 | Gem slot 1 unlocks (all gear slots) |
| 20 | Gem slot 2 unlocks (Head/Hands/Body) + star upgrade becomes available |
| 30 | Gem slot 2 unlocks (Legs only) |
| 40 | Gem slot 3 unlocks (Head/Hands/Body) + Rare max level |
| 60 | Gem slot 3 unlocks (Legs only) + Epic max level |
| 80 | Legendary max level |

**Critical rule:** Push all 4 pieces on a hero to lv10 before pushing any to lv20. First gem slots across all 4 pieces simultaneously outperform one piece at lv20.

**Critical rule:** Never equip freshly crafted Legendary gear until lv20. Epic gear outperforms Legendary below lv20.

---

## DISMANTLING

| Rarity | Tools returned |
|---|---|
| Rare | 50 |
| Epic | 250 |
| Legendary | 600 |

**Rule:** Always dismantle Rare gear immediately — 50 tools returned outweigh the value of an equipped Rare piece. Never dismantle Epic or Legendary without resetting first.

---

## STAR UPGRADE SYSTEM

Stars unlock substats. Requires gear at a minimum level AND duplicate pieces.

| Star | Minimum gear level | Duplicates | Magma Crystals | Legendary Crystals |
|---|---|---|---|---|
| Star 1 | 20 | 1 | 32 | 0 |
| Star 2 | 40 | 3 | 96 | 0 |
| Star 3 | 60 | 6 | 144 | 48 |
| Star 4 | 80 (Legendary only) | 10 | 0 | 320 |

**Max stars by rarity:** Rare = 2 | Epic = 3 | Legendary = 4

**Star substat values at max stars:**

| Substat | Rare max | Epic max | Legendary max |
|---|---|---|---|
| HP (all units health) | +0.9% | +1.5% | +3.0% |
| Damage (all damage) | +0.72% | +1.2% | +2.4% |
| Capacity (unit capacity) | +540 | +900 | +1,800 |
| Kill rate | +1.5% | +3.0% | +4.5% |
| Counter damage dealt | 0% | +2.1% | +4.5% |
| Counter damage taken reduction | 0% | +2.1% | +4.5% |
| Skill damage | 0% | 0% | +3.0% |
| Damage taken reduction | 0% | 0% | +2.4% |

**Note:** Lightning Crystals are listed as a gear upgrade material in the Theria calculator UI. Exact usage — which levels or stars require them — *[verify in-game]*.

---

## GEM SYSTEM

### Gem slot assignments

| Gear slot | Slot 1 | Slot 2 | Slot 3 |
|---|---|---|---|
| Head | Strategy | Strategy | Strategy |
| Hands | Hero | Hero | Hero |
| Body | Tactic | Tactic | Tactic |
| Legs | Strategy | Hero | Tactic |

Legs is the most flexible slot — one of each gem category.

### Gem categories

**Strategy gems** (Head + Legs slot 1) — troop stats:
- Unit attack %
- Unit defence %
- Unit health %
- Unit capacity (flat)
- Gathering speed %

**Hero gems** (Hands + Legs slot 2) — hero stats:
- Might
- Strategy
- Armor
- Siege
- All attributes

**Tactic gems** (Body + Legs slot 3) — skill damage:
- Active skill damage %
- Secondary strike skill damage %
- Passive skill damage %
- Turn-based skill damage %
- Healing effects %
- Normal attack damage %

### Gem tiers — 10 tiers (Common through Mythic IV)

| Tier | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Hero (Might/Str/Arm/Siege) | 0.9 | 1.35 | 2.0 | 3.0 | 4.5 | 6.85 | 10.35 | 15.75 | 23.6 | 36.0 |
| Hero All Attributes | 0.45 | 0.65 | 1.0 | 1.5 | 2.25 | 3.4 | 5.15 | 7.85 | 11.8 | 18.0 |
| Tactic (skill dmg %) | 0.3 | 0.45 | 0.7 | 1.0 | 1.5 | 2.3 | 3.45 | 5.25 | 7.9 | 12.0 |
| Strategy (unit atk/def %) | 0.4 | 0.6 | 0.9 | 1.35 | 2.0 | 3.05 | 4.6 | 7.0 | 10.5 | 16.0 |
| Strategy Health (unit hp %) | 0.2 | 0.3 | 0.45 | 0.68 | 1.0 | 1.53 | 2.3 | 3.5 | 5.25 | 8.0 |
| Strategy Capacity (flat) | 100 | 150 | 230 | 340 | 500 | 760 | 1150 | 1750 | 2630 | 4000 |

*[Gem upgrade costs between tiers — verify in-game or via Theria calculator]*

### Gem recommendations by hero role

| Role | Head (Strategy) | Hands (Hero) | Body (Tactic) | Legs |
|---|---|---|---|---|
| SW/PIK/CAV attack lead | Unit attack | Might | Active skill dmg | Unit attack / Might / Active |
| ARC attack lead | Unit attack | Strategy | Active skill dmg | Unit attack / Strategy / Active |
| Secondary strike support | Unit attack | Might | Secondary strike dmg | Unit attack / Might / Secondary |
| Turn-based DPS (Octavian) | Unit attack | Might | Turn-based dmg | Unit attack / Might / Turn-based |
| Recovery support | Unit health | All attributes | Healing | Unit health / Armor / Healing |
| Gathering hero | Gathering speed | Any | Any | Gathering / Any / Any |

**General rule:** Never use Siege gems on any combat hero. Unit capacity gems in Strategy slots are strong for march leads — directly increase troop count per march.

---

## GEAR INVESTMENT PRIORITY

1. All 4 pieces to lv10 on M1 heroes → first gem slots across the board
2. All 4 pieces to lv20 on M1 → second gem slots + star upgrade eligibility
3. Repeat for M2 before touching M3/M4/M5
4. Legendary gear: craft and hold at lv1 until you can push to lv20 in one session
5. Dismantle all Rare gear immediately on acquisition

---

## KNOWN GAPS

| Gap | Status |
|---|---|
| Lightning crystals — exact use (level/star requirement) | *[verify in-game]* |
| Gem upgrade costs between tiers | *[verify in-game or via Theria calculator]* |
| Cumulative forge tool totals (Rare/Epic/Legendary to max) | Estimated — verify |

---

*Source: aoem-calculator GearData.ts/GemsData.ts (MIT licence, juan_jm, Codeberg). Additional notes: Network Grey original content. Theria Games calculator confirmation: Jayson, Aug 2025.*
