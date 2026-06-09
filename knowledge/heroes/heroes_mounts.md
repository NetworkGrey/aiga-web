# AIGA Hero Reference — Mount System
## knowledge/heroes/mounts/heroes_mounts.md
**Version:** 1.0 | **Date:** June 2026
**Source:** Mount System Guide V2 (community) | aoem-calculator | AIGA session data

---

## OVERVIEW

Each hero equips one mount. Mounts provide base attribute bonuses and traits that enhance combat performance. No mount equipped is always worse than any wrong-temperament mount — equip something on every hero before worrying about quality.

**Epic mounts require hero level 40+ to equip.**
**Rare mounts can be equipped at any hero level.**

---

## MOUNT QUALITY TIERS

| Quality | Rarity | Colour | Base attributes | Attribute range |
|---|---|---|---|---|
| Courser | Common | Blue | 2 | +2 to +4 |
| Destrier | Epic | Purple | 2 | +5 to +9 |
| Skywing | Legendary | Gold | 2 | +10 to +16 |
| Celestial Charger | Mythical | Red | 3 | +18 to +25 |

Base attributes (Might / Armor / Strategy / Siege) stack directly with hero stats. Higher quality = stronger base. Offspring never exceed the attribute range ceiling of their tier.

---

## BREEDING RULES

- **Epic × Epic = Epic only** — trait improvement, cannot produce Legendary
- **Legendary × Legendary = Celestial Charger (Mythical)** — only path to Mythical
- Mounts can only breed with others of identical quality — no cross-quality breeding
- Both parent mounts are consumed in the process
- Maximum 100 breedings per session
- **Never mix temperaments when breeding** — always same × same temperament

**Minimum retention rule:** Destrier (Epic/Purple) is the minimum quality to retain. Always assign and lock hero mounts before any mass breeding session — Courser mounts will be consumed.

---

## TEMPERAMENT SYSTEM

Temperament determines what traits offspring inherit or mutate toward.

| Temperament | Speciality | Mutation rate | Best used on |
|---|---|---|---|
| Warbred | Might damage traits | 80.19% | Attack leads and damage supports |
| Alert | Strategy damage traits | 80.18% | Strategy-primary heroes |
| Fearless | Universal traits | 78.95% | March leads, rally-focused heroes |
| Protective | Healing/recovery traits | 80.17% | Support and recovery heroes |
| Docile | Trait preservation | 55% | Preserving specific valuable traits |
| Spirited | Random new traits | 55% | Generating new trait combinations |
| Mischievous | None | No effect | Discard |

**Temperament inheritance rule:** Breeding same × same gives the highest chance of matching offspring temperament.

---

## TRAITS BY TEMPERAMENT

### Warbred — Might Damage Traits

| Trait | Min effect | Max effect | Skill type |
|---|---|---|---|
| Overpower | Active skill Might damage +2% | +10% | Active skills |
| Gallant | Secondary strike Might damage +2% | +10% | Secondary strike |
| Valor | Passive skill Might damage +2% | +10% | Passive skills |
| Phalanx Breaker | Turn-based skill Might damage +2% | +10% | Turn-based skills |
| Fierce | Normal attack damage +4.5% | +22.5% | Normal attacks |

**Best Warbred trait by hero:**
- Musashi (active skill lead): Overpower
- Guan Yu (critical/normal attack): Fierce
- Josephine (attack support): Overpower or Valor
- Attila (double attack): Fierce

---

### Alert — Strategy Damage Traits

| Trait | Min effect | Max effect | Skill type |
|---|---|---|---|
| Spiritbond | Active skill Strategy damage +2% | +10% | Active skills |
| Stratagem | Secondary strike Strategy damage +2% | +10% | Secondary strike |
| Cunning | Passive skill Strategy damage +2% | +10% | Passive skills |
| Battlemaster | Turn-based skill Strategy damage +2% | +10% | Turn-based skills |

**Best Alert trait:** Spiritbond or Battlemaster for strategy-primary heroes (Theodora, Suleiman, Belisarius, Sun Tzu, Ramesses II).

---

### Fearless — Universal Traits

| Trait | Min effect | Max effect | Notes |
|---|---|---|---|
| Thunderbolt | Critical strike damage +2.7% | +13.5% | Offensive |
| Army Sunder | All damage types +1.8% | +9% | Universal offensive |
| Dustbane | Solo battle damage +2% | +10% | Solo PvP only |
| Tidebreaker | Rally battle damage +2% | +9% | **Rally — highest priority for rally players** |
| Bastion | Incoming damage reduction | — | Defensive — good for march leads |

**Priority:** Tidebreaker is the most valuable Fearless trait for alliance rally gameplay. Target for march leads used in rallies.

---

### Protective — Healing Traits

| Trait | Min effect | Max effect | Notes |
|---|---|---|---|
| Lifesaver | After recovery, damage taken -0.96% | -4.8% for 3s | Best for recovery support heroes |
| Renewal | Healing effect +2.3% | +11.5% | General healing boost |
| Healing Armor | Received healing +0.8% | +4% | Received healing boost |

**Best Protective trait:** Lifesaver for supports with recovery skills. Renewal for general support.

---

## MOUNT ASSIGNMENT BY HERO ROLE

| Hero role | Temperament | Target trait |
|---|---|---|
| SW attack lead (Musashi) | Warbred | Overpower |
| CAV attack lead (Lu Bu) | Warbred | Fierce or Valor |
| ARC attack lead (Mulan) | Warbred or Alert | Overpower (W) or Spiritbond (A) |
| PIK march lead (rally) | Fearless | Tidebreaker |
| Universal 3rd slot (Attila) | Warbred | Fierce |
| Strategy support (Theodora) | Alert | Spiritbond or Battlemaster |
| Recovery support (Justinian) | Protective | Lifesaver or Renewal |
| Gathering hero (Diao Chan) | Protective | Trait less critical |

---

## ADORNMENT SYSTEM

Each mount equips one adornment. Adornments provide additional combat bonuses beyond mount base stats and traits.

**Crafting:** 10 Meteorite Steel per adornment | Dismantling returns 5 Meteorite Steel (50% recovery)

Choose attack or defence variant per military specialty. Cannot equip both simultaneously.

### Upgrade levels and bonus thresholds

**Attack adornments:**
| Level range | Bonus type |
|---|---|
| 1-20 | Attack bonus +1%+ |
| 20-40 | Health bonus +0.5%+ |
| 40-60 | Skill damage increase +0.5%+ |

**Defence adornments:**
| Level range | Bonus type |
|---|---|
| 1-20 | Defence bonus +1%+ |
| 20-40 | Health bonus +0.5%+ |
| 40-60 | Skill damage taken reduction +0.5%+ |

**Upgrade materials:** Raw Iron (20-800 units per level, increases with level) | Chalcedony (1 per re-roll attempt for effect rarity upgrades)

### Re-roll system
Adornment effects can be upgraded through rarity tiers (Common through Mythical) using Chalcedony + Raw Iron. First tier upgrade is 100% success. Higher tiers have increasing failure chance and potential downgrades.

### Adornment priority
1. M1 heroes first
2. M2 heroes
3. M3/M4/M5 after primary marches are equipped

### Recommended adornments by hero type

| Hero type | Recommended adornment |
|---|---|
| SW lead (Musashi) | Attack — Swordsmen — Thunder or Wavebreaker |
| PIK lead | Attack or Defence — Pikemen — Secondary Strike (rare) or Resistance |
| CAV lead (Lu Bu) | Attack — Cavalry — Chain Slayer or Boiling Blood |
| ARC lead (Mulan) | Attack — Archers — War Prep or Lightning Strike |
| PIK support | Attack — Pikemen — Thunder or Blood Debt |

---

## MOUNT NAMING CONVENTION

| Prefix | Temperament |
|---|---|
| W | Warbred |
| F | Fearless |
| P | Protective |
| A | Alert |
| D | Docile |
| S | Spirited |
| M | Mischievous |

Format: `[ParentA_ID]-[ParentB_ID][generation]`
Example: W9 × W11 → W9-11a (first attempt), W9-11b (second attempt)

---

## LOCK / DISCARD RULES

| Action | Applies to |
|---|---|
| Lock immediately | All assigned mounts, breeding pairs, breeding reserves |
| Unlock to discard | Wrong temperament mounts with no breeding value |
| Never discard | Legendary mounts regardless of temperament; any mount with exceptional traits |

**Discard criteria:** Mischievous (no value), Docile with no valuable traits, Alert unless strategy heroes are in active marches, Spirited with no traits unless needed for mutation.

---

## MOUNT RESOURCE SOURCES

| Resource | Primary sources |
|---|---|
| Mount Whistles | Desolate Desert, Rally Against Tribes, Alliance Treasury, Merits Store, Empire Horse Range |
| Meteorite Steel | Desolate Desert, Mall, Rally Against Tribes events, Merits Store |
| Raw Iron | Desolate Desert, Mall, Rally Against Tribes, Merits Store |
| Chalcedony | Desolate Desert, Mall, Rally Against Tribes, Merits Store |

**Best free source:** Desolate Desert and alliance events — complete consistently for steady income.

---

## ANIMAL RESEARCH (BREEDING SKILL TREE)

| Research | Effect |
|---|---|
| Keen Eye for Steeds | Better mount discovery rates |
| Natural Advantage | Higher chance of superior base attributes from breeding |
| Legacy Inheritance | Inherited traits more likely to have high values |
| Exceptional Talent | Mutated traits acquire higher values more frequently |
| Bloodline Stability | Unlocks Adornment Workshop, increases fusion insight points |

**Priority:** Green path first (search proficiency and prophecy gain) before red path (combat stats). Focus on your primary march troop type path first.

---

*Source: Mount System Guide V2 (community guide). aoem-calculator. AIGA session data. Verify current values in-game — breeding rates and adornment costs may change with game updates.*
