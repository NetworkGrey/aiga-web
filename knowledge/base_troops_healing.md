# AIGA Base Reference — Troops & Healing
## knowledge/base/base_troops_healing.md
**Version:** 1.0 | **Date:** June 2026
**Source:** aoem-calculator TroopData.ts / HealingData.ts (MIT licence, juan_jm/aoem-calculator, Codeberg)

---

## TROOP SYSTEM

### Counter System

| Troop | Beats | Beaten by | Counter effect |
|---|---|---|---|
| Swordsmen | Pikemen | Archers | +30% damage dealt, +30% damage reduction |
| Pikemen | Cavalry | Swordsmen | +30% damage dealt, +30% damage reduction |
| Cavalry | Archers | Pikemen | +30% damage dealt, +30% damage reduction |
| Archers | Swordsmen | Cavalry | +30% damage dealt, +30% damage reduction |

**M2 (Pikemen) has no hard counter weakness** — safest march for unknown enemy compositions.

### Troop Stats Per Unit

| Tier | Power | Train time (s) | Food | Wood | Stone | Gold | MGE pts | MEE pts | Gather load |
|---|---|---|---|---|---|---|---|---|---|
| T1 | 1.0 | 10 | 80 | 20 | 0 | 0 | 2 | 30 | 45 |
| T2 | 1.3 | 14 | 100 | 30 | 30 | 0 | 3 | 50 | 60 |
| T3 | 1.7 | 19 | 140 | 40 | 40 | 40 | 5 | 70 | 75 |
| T4 | 2.2 | 28 | 235 | 55 | 55 | 55 | 10 | 100 | 90 |
| T5 | 2.9 | 43 | 340 | 80 | 80 | 80 | 20 | 160 | 105 |
| T6 | 4.2 | 75 | 470 | 110 | 110 | 110 | 50 | 280 | 120 |
| T7 | 6.0 | 130 | 650 | 150 | 150 | 150 | 100 | 500 | 135 |

*Note: T5 MEE pts — system prompt shows 160, multiplier analysis implies 200. [verify in-game]*

### Promotion Costs

Promoting troops from one tier to the next costs the **difference** between the two tiers.

Example — T3→T4 per troop: 95 food + 15 wood + 15 stone + 15 gold

| Promotion | Food | Wood | Stone | Gold |
|---|---|---|---|---|
| T1→T2 | 20 | 10 | 30 | 0 |
| T2→T3 | 40 | 10 | 10 | 40 |
| T3→T4 | 95 | 15 | 15 | 15 |
| T4→T5 | 105 | 25 | 25 | 25 |
| T5→T6 | 130 | 30 | 30 | 30 |
| T6→T7 | 180 | 40 | 40 | 40 |

### Critical Training Rules

- **Train the highest available tier directly** — promotions earn **zero** MGE/MEE points
- Promote during peace; train fresh during events
- Never promote during MGE/MEE — wasted event points
- Highest tier troop available depends on University military research completion

---

## HEALING SYSTEM

### Healing Cost Per Troop

All values are **per single troop**. Multiply by wounded count for totals.

| Tier | Time (min) | Food | Wood | Stone | Gold |
|---|---|---|---|---|---|
| T1 | 0.11 | 8 | 2 | 0 | 0 |
| T2 | 0.14 | 10 | 3 | 3 | 0 |
| T3 | 0.18 | 14 | 4 | 4 | 4 |
| T4 | 0.29 | 23 | 5 | 5 | 5 |
| T5 | 0.43 | 34 | 8 | 8 | 8 |
| T6 | 0.76 | 47 | 11 | 11 | 11 |
| T7 | 1.33 | 65 | 15 | 15 | 15 |

**Healing = ~10% of training cost at every tier. Always heal, never retrain.**

### Heal vs Train Comparison

| Tier | Heal food cost | Train food cost | Savings from healing |
|---|---|---|---|
| T3 | 14 | 140 | 90% |
| T4 | 23 | 235 | 90% |
| T5 | 34 | 340 | 90% |
| T6 | 47 | 470 | 90% |
| T7 | 65 | 650 | 90% |

### Bulk Healing — 10,000 Troops

| Tier | Food | Wood | Stone | Gold | Time |
|---|---|---|---|---|---|
| T4 | 230,000 | 50,000 | 50,000 | 50,000 | 2d |
| T5 | 340,000 | 80,000 | 80,000 | 80,000 | 3d |
| T6 | 470,000 | 110,000 | 110,000 | 110,000 | 5d 6h |
| T7 | 650,000 | 150,000 | 150,000 | 150,000 | 9d 4h |

### Bulk Healing — 50,000 Troops

| Tier | Food | Wood | Stone | Gold | Time |
|---|---|---|---|---|---|
| T4 | 1,150,000 | 250,000 | 250,000 | 250,000 | 10d |
| T5 | 1,700,000 | 400,000 | 400,000 | 400,000 | 15d |

### Hospital Management

- **Troops wounded beyond hospital capacity are permanently lost**
- Hospital must scale with total troop count
- At 500,000+ troops: hospital capacity should comfortably exceed largest single battle casualty estimate
- Upgrade hospital at TC11, TC16, TC21, TC28 milestones
- **Signs hospital is too small:** troops showing as lost (not wounded), hospital queue full after any major rally, wounded count exceeds capacity shown in city overview

**Hospital capacity from research (lv5):** +25,000 base capacity
**Additional capacity from VIP:** +10,000 per VIP level from VIP10 to VIP18

**During war:**
- Keep healing queue full at all times
- Prioritise highest tier troops first (T4+ most expensive to replace)
- Use healing speedups after heavy rally periods

**During peace:**
- Clear all wounded before next war phase
- Stock Food and Wood specifically — primary healing resources

**Food reserve rule:** Maintain Food stockpile to heal minimum 20-30% of total troop count between gathering runs. At 500,000 T4 troops = ~2.3M Food healing buffer.

---

*Sources: aoem-calculator TroopData.ts / HealingData.ts (MIT licence, juan_jm, Codeberg). Strategic notes: Network Grey.*
