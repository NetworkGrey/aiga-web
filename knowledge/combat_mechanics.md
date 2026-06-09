# AIGA Combat Reference — Mechanics & World Map
## knowledge/combat/combat_mechanics.md
**Version:** 1.0 | **Date:** June 2026
**Sources:** Van (YouTube, March 2026) | Theria Games — Roi B (Nov 2024) | Official AoEM | Community

---

## COUNTER SYSTEM

| Your troop | Beats | Beaten by |
|---|---|---|
| Swordsmen | Pikemen | Archers |
| Pikemen | Cavalry | Swordsmen |
| Cavalry | Archers | Pikemen |
| Archers | Swordsmen | Cavalry |

Counter advantage = **30% damage bonus dealt + 30% damage reduction received.** Always identify enemy troop composition before engaging when possible. M2 (Pikemen) has no hard counter weakness — safest march for unknown enemy compositions.

---

## OPEN FIELD PvP

### Pre-Fight Assessment

Before engaging any player, check two profile stats:

| Metric | What it signals |
|---|---|
| **Power** | Total account strength — troops, buildings, research, heroes |
| **Merits** | Accumulated PvP experience — earned through combat victories and damage |

**Reading the ratio:**
- High power + high merits: experienced fighter. Engage carefully.
- High power + low merits: strong account, little PvP experience. Favourable target.
- Low power + high merits: battle-hardened, likely punching above weight. Respect their experience.
- Low power + low merits: new or inactive. Low risk, low reward.

**How to check:** Tap player profile → compare power and merits. Visible on server leaderboard for broad comparison.

### Deck Slot Positioning

Slots 1 and 5 can scroll off-screen on average devices. Seconds lost scrolling during a fast engagement matter.

| Slot | Recommended role | Rationale |
|---|---|---|
| 1 | Secondary combat / counter march | Available but off-centre |
| 2 | Support march | Flanks primary on deployment |
| **3** | **Primary combat march** | **Always centre-screen — fastest access** |
| 4 | Support march | Flanks primary on deployment |
| 5 | Gathering or reserve | Least accessible |

Troops physically deploy in deck order — slot 3 spawns at front. Put your tankier march there if you want it absorbing first contact; your damage march if you want first strike.

### Commander Skill Manual Trigger

The commander skill auto-fires on a cooldown, but tapping the icon manually fires it earlier. In assassination-style open field engagements, tap immediately on deployment — do not wait for auto-trigger. Approximately 1 second advantage in tight fights.

### Auto-Return Toggle

After each fight, troops default to returning to citadel automatically. During active PvP:
- Turn auto-return **off** — troops stay in the field between engagements
- Turn auto-return **back on** for peace periods, gathering sessions, or overnight

### Peace Shield Cooldown

Peace shield cannot be activated while troops are in combat or returning. Activation is available **15 minutes after all battle actions halt.**

---

## STAMINA

- 5 stamina per march per attack
- 3-march attack = 15 stamina
- Rallies = **zero stamina cost**
- Tribe attacks are the primary stamina sink during peace config
- Depletes quickly during active tribe grinding — plan M3/M4 rotations around stamina recovery

---

## AUTO-BATTLE

Auto battle sends troops to attack tribes or world targets automatically.

**Rules:**
- Hospital must not be full — wounded troops die instead of being hospitalised if hospital is at capacity
- Always check hospital capacity before extended auto-battle sessions
- Auto-battle is most efficient for tribe grinding with M3/M4 during peace config
- Do not leave auto-battle running overnight without checking hospital capacity first

---

## MERITS

Merits accumulate through PvP activity and **never reset**. They function as a permanent lifetime combat record. The merits store resets **daily** — spend every day without exception.

**Merit store priority:**

| Priority | Item |
|---|---|
| 1 | Training speedups (highest value) |
| 2 | XP Tomes |
| 3 | Food (only if bottlenecking training queue) |
| 4 | Mount materials (whistles, Meteorite Steel, Raw Iron, Chalcedony) |
| 5 | Wood / Stone / Gold (lowest) |

---

## WORLD MAP

### Coordinate System

Every map location has X and Y coordinates. Type coordinates directly into map search to jump instantly. Share coordinates in alliance chat for rally targets, hive relocation, and attack planning. Eliminates confusion from vague directional descriptions.

### Fog of War

Unexplored areas are covered in fog. Sending scouts reveals terrain and enemy positions. Scout routes and target areas before major offensives — do not attack blind.

### Birth Region Strategic Elements

| Element | Benefit | Priority |
|---|---|---|
| **Cities** | Capturing enhances resource production efficiency | Medium — requires rally to occupy |
| **Crossings** | Controls travel routes between regions | **High — primary territorial objective** |
| **Passes** | Controls movement between regions | High — gates to Kingsland |
| **Monuments** | Improve specific troop type combat attributes | Medium — take if adjacent to hive |

**Crossings** are the highest-value contested birth region objectives. Controlling the crossing nearest your hive significantly reduces vulnerability to cross-region raids. Establish crossing control before passes open to Kingsland.

### Terrain

- **Mountains** — impassable or slow movement, create defensive lines
- **Rivers** — movement barriers, cross only at designated crossings
- **Forests** — affect movement and concealment

Hive positioning relative to terrain matters. A hive backed against a river with a controlled crossing in front is significantly harder to raid than an open-field hive.

### Additional Map Features

| Feature | Effect |
|---|---|
| Holy Sites | Alliance control objectives — grant benefits *[verify in-game for full mechanics]* |
| Ruins | Interact to receive temporary buffs *[buff types — verify in-game]* |
| Alliance Buildings | Fortresses and Towers — defensive structures alliances build in territory |

### Passes — Server Progression Gate

Passes open progressively over approximately **two months** from server launch. Each new pass grants access to new territories and resources. Early development in the birth region determines readiness when passes open. Alliances that develop quickly are better positioned when Kingsland becomes accessible.

---

## HIVE STRATEGY

- Hive in the birth region should be positioned relative to natural terrain (river, mountain backing)
- Closer to the Imperial City = better defensive positioning in Golden Expedition
- Sub-strongholds extend territorial reach into the resource region — build connected to the main stronghold
- Flags expand alliance territory — each flag must be built on land connected to strongholds or other flags

---

## TERRITORY — ALLIANCE STRUCTURES

| Structure | Function | Notes |
|---|---|---|
| Alliance Stronghold (Main) | Foundation of territory — can be built anywhere accessible | Must be connected; sub-strongholds connect to main or each other |
| Alliance Stronghold (Sub) | Built in resource region | Must be connected during construction; connection not required after |
| Alliance Flags | Expand territory | Must connect to stronghold or existing flag; higher cost in resource region and Imperial City region |
| Alliance Gathering Center | Grants gathering speed bonus | 1 per alliance; cannot be attacked during operation |
| Towers | Defensive structure | Controllable after reinforcing; power caps at 10K reinforcement |

**Territory building categories:** Politics / Science / Economy / Military / Faith / Facility — each with up to 7 levels, each boosting the corresponding alliance research speed.

**City types:** Common City | River Crossing | Mountain Fort

---

## IMPERIAL CITY

Controlling the Imperial City grants the victorious alliance leader the ability to appoint a **King**.

**Event structure:**
- Clash duration: 4 hours
- Win condition: First alliance to occupy for 1 hour, OR alliance with longest total occupation time
- Entry requirement: Alliance territory must border the Imperial City
- Sun Legions spawn inside during the event and attack all governors — additional hazard

**Sacred Towers** — four surrounding towers, each grants +20% attack and defence to the matching troop type for troops inside:

| Tower | Buff |
|---|---|
| Pike Sacred Tower | Pikemen attack + defence +20% inside IC |
| Sword Sacred Tower | Swordsmen attack + defence +20% inside IC |
| Cavalry Sacred Tower | Cavalry attack + defence +20% inside IC |
| Arrow Sacred Tower | Archers attack + defence +20% inside IC |

**AIGA advisory:** Sacred Tower control is a key pre-entry tactical objective. Capture the tower matching your primary march type before entering. Alliance coordination on tower assignment is critical.

---

## CITY CLASH

Weekly event. Alliances compete to occupy cities across the world map.

- Attacking a city does **not** require territory adjacency
- Last alliance to hit when city durability reaches 0 claims it
- Leaving or disbanding during the event is prohibited
- Win condition: occupy for the stipulated duration (clash ends immediately on win)

**Landmark occupation buffs (examples):**

| City | Buff |
|---|---|
| City of Shelter | All Unit Types' Defence +5% |
| City of Honor | All Unit Types' Health +5% |
| City of Beauty | Might Damage +5% |
| Acropolis of Daybreak | Strategy Damage +5% |

**AIGA advisory:** For rally-focused alliances, prioritise cities with damage buffs over health/defence buffs.

---

## GOLDEN EXPEDITION

Cross-kingdom invasion event where your alliance enters and fights in an enemy kingdom's territory.

- Enemy players can teleport to **any available spawn point** in their kingdom — not just near flags or forts
- Hive positioning closer to the Imperial City gives better defensive positioning during Golden Expedition
- Imperial City capture in GE: adds 20% of enemy's total war stage points to your score
- Taking the Imperial City does **not** guarantee winning — cumulative points across all stages determine victory
- Full Golden Expedition rules and scoring *[verify in-game — not fully documented]*

---

## APEX ARENA

| Detail | Info |
|---|---|
| Access | Expedition tab → Apex Arena |
| What you practice | Set offensive and defensive lineups — fight other governors |
| Rewards | Daily and weekly rewards based on rank |
| Resource risk | No permanent troop loss |

**AIGA recommendation:** Always check battle reports after Apex Arena fights. The details tab shows exact skill activations, damage dealt, healing received — fastest way to identify march weaknesses without risking real troops.

---

## BATTLEFIELD SURVIVOR

Standalone rogue-like mini-game mode. Play as Josephine on a battlefield. Not related to march composition or account progression.

- Collect idle rewards daily — non-negotiable
- Do not over-invest time if main account has higher-priority activities
- Hero levels, gear, and skills from the main game **do not apply** in this mode

---

## KNOWN GAPS

| Gap | Status |
|---|---|
| Holy Sites full mechanics | *[verify in-game]* |
| Golden Expedition full scoring and rules | *[verify in-game]* |
| Active combat window duration (90 min claim by community — verify) | *[verify in-game]* |
| Ruins buff types | *[verify in-game]* |

---

*Sources: Van (YouTube, March 2026 — deck positioning, commander skill trigger, auto-return toggle, merits, hero gift boxes, Arabs civ). Theria Games, Roi B (Nov 2024 — world map mechanics). Official AoEM Global Launch Show (TiMi Studio Group). Community.*
