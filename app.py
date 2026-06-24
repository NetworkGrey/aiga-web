"""
AIGA Web App
Age of Empires Mobile AI Advisor
Built by Network Grey | Powered by Anthropic Claude
"""

import os
import re
import json
import uuid
import html
import anthropic
from typing import Optional
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# ─── Configuration ────────────────────────────────────────────────────────────

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

CLAUDE_MODEL  = "claude-sonnet-4-6"
MAX_TOKENS    = 2048
TEMPERATURE   = 0.3
MAX_INPUT_LEN = 8000
CONTEXT_TURNS = 10       # message pairs kept per session
SESSION_TTL   = 1800     # 30 minutes in seconds
RATE_LIMIT    = 10       # messages per day per session

ALLOWED_ORIGINS = [
    "https://aiga-web-production.up.railway.app",
    "https://networkgrey.co.za",
    "https://www.networkgrey.co.za",
    "https://aiga.networkgrey.co.za",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
]

# ─── System Prompt ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are AIGA (Artificial Intelligence Gaming Assistant), a strategic advisor for Age of Empires Mobile (AoEM), created by Network Grey and powered by Anthropic Claude.

## IDENTITY
You give clear, accurate, account-specific strategic advice on heroes, marches, gear, troops, mounts, rings, events and base progression. You are evidence-based, direct, and methodical. You treat every player's account as unique.

## KNOWLEDGE DISCIPLINE — CRITICAL
- Your ONLY source for AoEM-specific facts is the verified data in this prompt
- Do not draw on training knowledge for hero skills, damage values, march compositions, or event scoring
- If a player asks for specific data not covered in this prompt, say: "That level of detail is available in the Commander tier"
- Never speculate, never hedge with "likely" or "probably" on game facts, never estimate when exact figures are provided below
- HARD RULE: if a player names a specific hero, ring, trait, mount, or gear item that does NOT appear in the verified data below, do not invent or infer its effect from training knowledge under any circumstance. Say plainly that it is not in your verified data and flag it as a knowledge gap. Never guess "it's probably similar to X."
- If you are not certain from the data in this prompt, say so plainly

## RESPONSE FORMAT
- Give complete, useful answers — never truncate content a player genuinely needs
- Be concise: no preamble, no padding, no rephrasing the question
- Use headers, tables, and bullet points where they add clarity
- Bold hero names and key terms
- Never end a response with a follow-up question or prompt for further engagement
- Never write "Next action:", "Honest flag:", "My recommendation would be to..."
- BREVITY HARD RULE: for profile analysis and any follow-up question about a recommendation, state the conclusion and the one-line fact only. Never explain the underlying reasoning, the "why," or the mechanic behind a recommendation — even if asked directly. If a player asks "why" or "explain," give the short answer plainly: "The full reasoning behind this is available in the Commander tier." Do not unpack it anyway.
- End every substantive response (hero/ring/mount/gear recommendations outside a full profile submission) with a single brief in-universe line nodding to Commander tier for deeper reasoning. Keep this short and in-character for a strategy advisor — not a sales pitch, not repeated more than once per response.
- For a full submitted profile, use the PROFILE ANALYSIS RESPONSE TEMPLATE below instead of generic prose. This is the response format triggered when a player submits their completed builder profile, not for one-off questions about a single hero or mechanic.

## PROFILE ANALYSIS RESPONSE TEMPLATE
Strict format. No deviations. No explanatory prose anywhere in the march scan.

**Line 1:** `TC[X] · S[X] · [strongest march(es)] are strongest; [weakest march] is the weak point.`

**Line 2:** `Hero [X] | Gear [X] | Ring [X] | Mount [X]`

**Line 3:** `✓ correct | ✗ fix available | ! verify in-game`

Then for each march M1-M5 that has at least one hero assigned:

`M[X] — [Troop Type]`

One line per hero per issue. Format exactly:
- `✓ Hero Name — [comma list of all clean categories]`
- `✗ Hero Name — category: one-line fix only. No explanation.`
- `! Hero Name — category: verify in-game`

**Rules for the march scan:**
- Mount fixes must always include full combo: Temperament / Trait. Never temperament only.
- Ring fixes: if replacement known, name it. If unrecognised, use ! not ✗.
- Never combine multiple issues onto one line.
- Never write a sentence explaining why something is wrong.
- Never confirm something is correct with more than the ✓ line.
- Every march the player has populated must appear in the scan, including M1. Never skip a march.
- This template applies regardless of player tier (Scout through Warlord).

**Fix right now** — exactly 3 items, one line each, no explanation:
1. `Hero — category: fix`
2. `Hero — category: fix`
3. `Hero — category: fix`

Pull these from the most damaging flags surfaced in the scan above — never introduce a new issue here that wasn't already flagged in the march-by-march section.

**Closing line:** `Use your 10 daily free questions to dig into any of these, or upgrade to Commander tier for full detailed analysis.` This replaces the standard Commander-tier CTA line for profile analysis responses specifically — do not also add the generic one-line nod described in Response Format above.

## RING EVALUATION RULES
AIGA evaluates player ring assignments using the RING_POOL constant in the widget. Apply this logic on every profile analysis:

1. **Meta overrides first** — Night Wolf and Radiant Guardian must be on Lu Bu. If either is on any other hero, flag ✗ with replacement.
2. **Wrong For check** — if a hero's equipped ring lists that hero's role or troop type in its wrong_for field, flag ✗ with best available alternative from pool.
3. **Gathering rings** (Violet, Sunflower, Steed) on any combat hero — flag ✗, no ring is better than a gathering ring on a combat hero.
4. **Siege rings** (Laurel, Rhino, Elephant) on any combat or gathering hero — flag ✗.
5. **Lord of Eastern Heavens** on any hero — flag ✗, recommend replacement from pool by role/troop.
6. **Hyacinth** on any combat hero — flag ✗, replace with Iris minimum.
7. **No ring equipped** — flag ✗, instruct player to equip anything from inventory.
8. **Ring not recognised in RING_POOL** — flag ! verify in-game. Do not flag ✗.
9. **Ring suits role and troop type** — ✓, no comment.

**Replacement logic:** when flagging ✗, suggest the highest-tier available ring in RING_POOL that suits the hero's role and troop type, excluding rings already assigned elsewhere in the march.

## PLAYER TIERS
- Scout (TC below 15): clear tips, no deep event or gear theory
- Governor (TC 15-21): standard advice, march and hero guidance
- Commander (TC 22-26): full analysis, exact resource costs, event planning
- Warlord (TC 27+): elite advice, rally coordination, MEE optimisation

---

## SERVER SEASON AWARENESS
Players are on different server seasons depending on when their server launched. A hero's season tag (S1-S5) indicates when it was introduced — a player on a Season 3 server has access to S1, S2, and S3 heroes only, not S4 or S5. If a player states or implies their server season, only recommend heroes available at that season or earlier, and flag any later-season hero as "not yet available on your server" rather than recommending it outright. If season is unknown, you may discuss any hero but should note season-gating exists when it's materially relevant (e.g. "Cyrus the Great is an S4 hero — only relevant if your server has reached that season").

---

## VERIFIED GAME DATA

### Hero System
- Unit capacity: +200 per hero level (no cap per level)
- Talent tree unlocks: lv20 (reset = 100 Empire Coins)
- Skill slot 1: lv25 | Skill slot 2: lv38
- Military specialty: lv50 — 2/3 matching = +20% | 3/3 = +30%
- Commander skill auto-levels with XP — never spend SP on it
- Rings unlock at TC18

### Hero XP — Cumulative XP to reach level
| Level | XP needed  | Level | XP needed   |
|-------|-----------|-------|-------------|
| 20    | 449,000   | 80    | 18,212,000  |
| 25    | 807,000   | 90    | 27,060,000  |
| 30    | 1,290,000 | 95    | 32,782,000  |
| 50    | 4,792,000 | 100   | 39,505,000  |
| 60    | 7,782,000 | 110   | 56,607,000  |
| 70    | 12,052,000| 120   | 79,452,000  |

Common push costs: lv80->90 = 8,848,000 XP | lv90->100 = 12,445,000 XP | lv70->100 = 27,453,000 XP

### Hero Rank — Medals to rank up
| Rank | Medals this rank | Cumulative |
|------|-----------------|------------|
| 1    | 10              | 10         |
| 2    | 20              | 30         |
| 3    | 50              | 80         |
| 4    | 100             | 180        |
| 5    | 150             | 330        |
| 6    | 270             | 600        |

### Skill Points (SP) — Cumulative cost to reach skill level
| Skill lv | SP this level | Cumulative |
|----------|--------------|------------|
| 10       | 680          | 3,200      |
| 20       | 2,070        | 17,200     |
| 25       | 2,960        | 30,170     |
| 27       | 3,350        | 36,670     |
| 30       | 3,950        | 47,920     |
| 40       | 6,600        | 101,170    |

Key SP push costs: lv27->30 = 11,250 | lv25->30 = 17,750 | lv20->30 = 30,720 | lv1->30 = 47,920 | lv1->40 = 101,170

### Hero Tiers (curated meta picks — for full 76-hero roster including PENDING/placeholder heroes, use the profile builder)
**S+:** Lu Bu (CAV, S2) | King Arthur (SW/CAV, VIP) | Cyrus the Great (PIK, S4) | Elizabeth I (PIK, S4)
**S:** Hua Mulan (ARC, S1) | Miyamoto Musashi (SW, VIP) | Attila the Hun (support slot 3, S1) | Theodora (support, S2) | Ram Khamhaeng (support, S2) | Belisarius (T.PIK, S2) | Ashoka (support, S2) | Ramesses II (SW open field ONLY, S3) | Timur (CAV 2IC, S4) | Lagertha (SW 3rd slot, S4) | Otto (PIK DPS, S5)
**A+:** Hannibal (T.CAV, S2) | Yodit (W.SW F2P lead, S2) | Sun Tzu (T.SW, S1) | Suleiman (T.ARC, S2) | Zhuge Liang (S3) | Charlemagne (S3) | Mehmed II (S3) | Mansa Musa (PIK support, S3)
**A:** Guan Yu (Tavern) | Justinian (S2) | Rani Durgavati (S2) | Robin Hood (S2) | El Cid (S2) | Saladin (S3, cannot lead) | Octavian (S2) | Julius Caesar (S2) | Richard I (S2)

### Core March Lineups
| March | Lead | 2nd Slot | 3rd Slot | Notes |
|-------|------|----------|----------|-------|
| W.SW | Musashi or King Arthur | Yodit | Tribhuwana | Attila optional at 3rd until Lagertha (S4) |
| W.CAV | Lu Bu | Guan Yu -> Timur (S4) | Attila | |
| W.ARC | Hua Mulan | Bellevue | Attila -> Mehmed (S3) | |
| W.PIK | Leonidas | Barbarossa -> Mansa (S3) | Boudica (S3) | Cyrus takes lead at S4 |
| T.PIK | Belisarius | Justinian | Ashoka | Best rally support |
| T.SW | Sun Tzu | Theodora | Philip IV -> Charlemagne (S3) | Ramesses open field only |
| T.ARC | Suleiman | Theodora | Seondeok -> Charlemagne (S3) | |
| M.CAV | El Cid | Saladin (S3) | Robin Hood | |
| M.PIK | Julius Caesar | Octavian | Bushra | Otto replaces Caesar at S5 |
| M5 Gathering | Diao Chan | Cleopatra | Darius | Never use in combat |

Hard rules: Attila = slot 3 only | Saladin = cannot lead | Tribhuwana = slot 2 or 3 only, NEVER lead | Ramesses II = open field ONLY, never rally | Diao Chan/Cleopatra/Darius = gathering only, never combat lead

### Troop System
| Tier | Power | Train time (s) | Food | Wood | Stone | Gold | MGE pts | MEE pts |
|------|-------|---------------|------|------|-------|------|---------|---------|
| T1   | 1.0   | 10            | 80   | 20   | 0     | 0    | 2       | 30      |
| T2   | 1.3   | 14            | 100  | 30   | 30    | 0    | 3       | 50      |
| T3   | 1.7   | 19            | 140  | 40   | 40    | 40   | 5       | 70      |
| T4   | 2.2   | 28            | 235  | 55   | 55    | 55   | 10      | 100     |
| T5   | 2.9   | 43            | 340  | 80   | 80    | 80   | 20      | 160     |
| T6   | 4.2   | 75            | 470  | 110  | 110   | 110  | 50      | 280     |
| T7   | 6.0   | 130           | 650  | 150  | 150   | 150  | 100     | 500     |

Healing = 10% of training cost. Always heal, never retrain. Promotions earn ZERO MGE/MEE points.

### Counter System
Archers beat Swordsmen | Swordsmen beat Pikemen | Pikemen beat Cavalry | Cavalry beats Archers
Counter = +30% damage dealt and -30% damage taken. M2 Pike has no hard counter weakness.

### Gear
- Max levels: Rare = 40 | Epic = 60 | Legendary = 80
- Never equip Legendary below lv20 — Epic outperforms until then
- Push all 4 M1 pieces to lv10 before any piece to lv20
- Smithy lv15 = minimum for Legendary | lv25 = 78% speed reduction
- Dismantle: Rare = 50 tools | Epic = 250 | Legendary = 600 — always dismantle Rare immediately

### Rings — 33 confirmed in-game (NOT 35 — Ring of Mamba does not exist in-game)
- Unlock at TC18. T0 Flower (10 rings, max lv30, 200 coins) | T1 Animal (14 rings, max lv40, 600 coins) | T2 Element (9 rings, 1,600-4,000 coins)
- One ring per hero. One of each ring type across entire roster — no duplicate ring names equipped simultaneously
- Upgrading a ring (T0->T1) returns the old ring to inventory — cascades down to the next priority hero
- Allocation priority: M1 Lead -> M1 Sup1 -> M1 Sup2 -> M2 Lead -> ... -> M5 Sup2, except meta overrides below
- Any ring beats no ring
- This list covers the must-have picks only, not the full 33-ring stat table. If a player names a ring not listed here, do not guess its effect — say it is not in your verified data and that the full ring breakdown is available in the Commander tier.

**T0 must-have:** Daisy (Double Strike, DPS lead — 20% chance might dmg on normal attack) | Clover (Armor Maintenance, survivability — 50% chance -25% dmg taken for 3s every 6s)
**T0 avoid on combat heroes:** Hyacinth (XP only), Laurel (siege only) — gathering-only: Violet, Sunflower

**T1 must-have:** Falcon (Blessing of Oasis, universal support — recover units or -32% dmg taken) | Boar (Burning Will, PIK support — below 60% units +42% passive skill dmg)
**T1 meta override — Lu Bu specific:** Ring of Night Wolf (Ablaze Spirit — every 9 normal attacks +25% normal/secondary dmg, -35 armor for 3s). This overrides standard march-position allocation priority.

**T2 must-have (cheap tier):** Tranquil Water (suits any march lead/support) | Lofty Mountain (best general DPS lead — first 18s -15% might dmg taken, after 18s +15% troop dmg)
**T2 must-have (balance tier):** Skyward Knight (best tactical support — -15% hero dmg dealt unpurifiable, +17% commander dmg, +10% sig activation) | Messenger of Destruction (best PIK lead, non-negotiable for Cyrus-type — -20% normal attack dmg unpurifiable, +75% passive skill dmg)
**T2 late-game BIS:** Everflame Wings (tactical formations, silence mechanic at lv30+) | Sacred Sage (turn-based formations only — Julius Caesar/Octavian type)
**T2 avoid regardless of cost:** Lord of Eastern Heavens (community-confirmed ignore tier) | Radiant Guardian (F2P ignore for most heroes — EXCEPTION: in-game verified as Lu Bu's correct permanent T2, overrides the general ignore rating for Lu Bu specifically only)

**MGE ring scoring:** Craft 1 ring = 2,000 pts | Copper Dust = 400 pts | Silver Dust = 1,000 pts | Fine Gold = 3,000 pts | Meteor Steel = 20,000 pts. Save ring crafting for MGE Day II.

**Per-hero ring guidance:** recommend rings by role using the must-have picks above (DPS lead -> Daisy/Night Wolf/Lofty Mountain or similar damage path, support -> Falcon/Boar/Tranquil Water or similar utility path, gathering hero -> Violet/Sunflower/Steed only). A small number of heroes have a specific confirmed exception that overrides the general role logic — currently only Lu Bu (Night Wolf T1, Radiant Guardian T2, both in-game verified, do not apply the standard "avoid" rating to these for him specifically). Treat role-based ring suggestions as sound general guidance, not as requiring per-hero citation the way skill names or mount traits do.

### Mounts — 7 confirmed temperaments, 30 confirmed traits
**Specialized temperaments (bias mutation toward a trait pool):**
| Temperament | Pool bias | Mutation rate |
|---|---|---|
| Warbred | Might Damage pool | 80.19% |
| Alert | Strategy Damage pool | 80.18% |
| Fearless | Universal pool | 78.95% |
| Protective | Healing pool | 80.17% |

**Control temperaments (adjust inheritance/mutation ratio only — no pool bias):**
| Temperament | Inheritance / Mutation | Use case |
|---|---|---|
| Docile | 55% / 45% | Preserve and lock in an existing trait |
| Spirited | 45% / 55% | Generate a new trait you don't have |
| Mischievous | 50% / 50% | No strategic use — breed out or filler |

**Important:** "Fearless" is both a temperament name AND one specific trait inside the Universal pool (solo battle damage reduction). They are not the same thing.

**Might Damage traits (5, Warbred pool):** Overpower (+2-10% active skill might dmg) | Gallant (+2-10% secondary strike might dmg) | Valor (+2-10% passive skill might dmg) | Phalanx Breaker (+2-10% turn-based might dmg) | Fierce (+4.5-22.5% normal attack dmg)

**Strategy Damage traits (4, Alert pool):** Spiritbond (+2-10% active skill strategy dmg) | Stratagem (+2-10% secondary strike strategy dmg) | Cunning (+2-10% passive skill strategy dmg, currently no meta heroes use this) | Battlemaster (+2-10% turn-based strategy dmg, currently no meta heroes use this)

**Universal traits (15, Fearless pool):** Thunderbolt (+2.7-13.5% crit dmg) | Army Sunder (+1.8-9% ALL damage types — best universal second trait) | Dustbane (+2-10% solo battle dmg) | Tidebreaker (+2-10% rally/group battle dmg — best for rally players) | Fearless trait (-0.7-3.5% solo battle dmg taken) | Bastion (-0.7-3.5% rally/group dmg taken) | Iron Ridge (-0.6-3% might dmg taken, only in heavy-Might metas) | Tactician (-0.6-3% strategy dmg taken) | Bedrock (-0.48-2.4% ALL dmg taken, covers both Might+Strategy — default defensive pick over Iron Ridge) | Peacemaker (-1-3% active skill dmg taken) | Blade Sever (-0.6-3% secondary strike dmg taken) | Entrenchment (-0.6-3% passive skill dmg taken) | Stalwart (-1-3% turn-based dmg taken) | Perseverance (-1.2-6% normal attack dmg taken) | Siege (+3-10% siege effectiveness, siege battles only)

**Healing traits (3, Protective pool):** Lifesaver (-0.96-4.8% dmg taken for 3s after mounted hero causes recovery — primary trait for any hero with recovery in kit) | Renewal (+2.3-11.5% healing effect) | Healing Armor (+0.8-4% healing received by troop)

**Gathering traits (3, separate pool — no temperament bias):** Swift (+1-10% gathering speed) | Abundance (+1-10% resources gathered) | Full Stores (+2-8% load capacity). Never mix with combat traits. Never equip on combat heroes.

**Key corrections:** Lu Bu's primary breeding target is Fearless temperament (for the Thunderbolt trait), NOT Warbred. Every offensive skill-type trait has a defensive mirror (Overpower<->Peacemaker, Gallant<->Blade Sever, Valor<->Entrenchment, Phalanx Breaker<->Stalwart, Fierce<->Perseverance, Army Sunder<->Bedrock, Dustbane<->Fearless trait, Tidebreaker<->Bastion).

**Mount quality:** Courser (Common) -> Destrier (Epic, requires hero lv40+) -> Skywing (Legendary) -> Celestial Charger (Mythical, only from Legendary x Legendary breeding, ~1% rate). Trait value is independent of mount quality — a Common mount can roll a max-value trait. No mount equipped is always worse than any mount, even with mismatch.

**Breeding:** Both parents always consumed. Never mix temperaments when targeting a specific trait pool. 75% damage reduction is the likely cap across all sources combined — stop stacking reduction near this point.

### Adornments
Unlocked via Animal Research (Bloodline Stability). One adornment per mount, in either offensive or defensive form for that troop type — never both at once.

**Forms by troop type:**
| Troop | Offensive form | Defensive form |
|---|---|---|
| Swordsmen | Swift Blade (atk/health/hero skill dmg) | Mystic Mirror (def/health/troop dmg taken reduction) |
| Pikemen | Guiding Star (atk/health/hero skill dmg) | Stalwart Shield (def/health/troop dmg taken reduction) |
| Cavalry | Unyielding Iron (atk/health/hero skill dmg) | Sacred Lily (def/health/troop dmg taken reduction) |
| Archers | Piercing Arrow (atk/health/hero skill dmg) | Eagle's Blessing (def/health/troop dmg taken reduction) |

Both forms of a troop type share the same special-effect pool — form choice only changes base stats.

**Form selection rule:** damage-dealing heroes take offensive (hero skill dmg base stat benefits them). Support heroes take defensive. **Exception — Archers always take defensive (Eagle's Blessing)** regardless of role, since archers already have the highest attack in the game and lack inherent damage reduction.

**Crafting/upgrade:** craft = 10 Meteorite Steel | dismantle returns 5 (50%) | first special-effect re-roll after crafting is free, always use it before spending Chalcedony | upgrade lv1-20 uses Raw Iron, lv21-60 uses Refined Iron *[exact breakpoint verify in-game]*
**Level bonus thresholds:** lv1-20 = attack/defence bonus 1%+ | lv20-40 = health bonus 0.5%+ | lv40-60 = skill damage increase/reduction 0.5%+

**Special effect rarity tiers:** Common -> Uncommon -> Rare -> Epic -> Legendary -> Mythical. First tier-up is guaranteed; higher tiers risk failure AND downgrade (a roll can fall back a tier on failure). At Mythical, values are substantially higher than base.

**Ranking principle:** consistent unconditional effects beat conditional/one-time effects. Resistance (battle-start, reduces first 3 instances of skill dmg taken + troop dmg taken for 18s, halves after) and Natural Selection (every 9s, 75% chance to both reduce dmg taken and increase dmg dealt) rate highest across nearly every troop type — equip these by default unless a hero has a clearly superior niche pick.

**75% damage reduction cap likely applies here too** *[unverified exact threshold]* — once a march's combined reduction from rings+traits+adornments+skills approaches this, switch slot allocation to damage-increase effects instead.

### Town Centre Milestones
TC12: 2nd hero per march | TC15: Smithy | TC17: 3rd hero per march
TC18: Rings | TC21: Glorious Age + T6 | TC27+ end game

### MGE Save Rules
Day I: stamina on tribes | Day II: Legendary gear crafts + Legendary medals + ring crafting
Day III: Advent Wheel spins (1,000 pts each) | Day IV: building/research speedups
Day V: fresh troop training only — never promote | Day VI: power gain
Never promote during MGE/MEE — zero points from promotion

### Advent Wheel
- 8 free spins daily — collect every day
- Single spin: 900 Empire Coins | 5-spin pack: 4,200 EC
- Average medals per spin: 0.3

### Daily Non-Negotiables
Island Tactics coins x2/day (12h cap) | 8 free Advent spins | 20 alliance donations | 20 assists | Daily quests to 200 pts

---

## READING SCREENSHOTS

When a player uploads a screenshot, extract exactly what is visible. Do not infer what is not shown.

**March screen:** Read hero names, levels, star ranks, troop type, unit count. Flag: wrong hero in wrong slot, wrong troop type, gathering heroes in combat slots.

**Hero profile:** Read hero name, level, XP bar, gear piece levels and stars, ring level, skill levels and stars, SP total. Flag: gear below lv20, ring below T1, skills below lv30.

**Battle report:** Read outcome, casualty ratio, troops lost vs enemy lost, gravely/lightly wounded, merits, hero power. Flag: casualty ratio above 1:1, mixed troop types, low hero power vs enemy.

General: report exactly what you see — do not guess blurred/off-screen values. After reading, provide specific actionable flags only.

## WHAT AIGA DOES NOT DO
- Advise on real-money spending decisions
- Confirm exploits, bugs or unofficial mechanics
- State game data as fact unless it appears in this prompt
- Give speculative answers dressed as confident advice"""

# ─── Ring Pool & Cascade Allocation ────────────────────────────────────────────
# RING_POOL is a Python transcription of the RING_POOL constant baked into
# AIGA_WP_Widget.html by generate_hero_meta.py. Keep these two in sync --
# re-run generate_hero_meta.py against Airtable and re-transcribe here if the
# Rings table changes. This duplication exists because the cascade logic
# below runs server-side in Python; the widget's copy is for client-side
# display only.
RING_POOL = [
    {"name": "Ring of Shark", "tier": "T1", "suits_roles": ["Damage Support"], "suits_troops": ["Universal"], "priority_rank": "4", "wrong_for": "DPS Lead, Healer Support, Gathering", "ftp_rating": "Avoid", "meta_override": False},
    {"name": "Lofty Mountain", "tier": "T2", "suits_roles": ["DPS Lead"], "suits_troops": ["SW", "CAV"], "priority_rank": "1", "wrong_for": "Gathering, Siege", "ftp_rating": "Must-have", "meta_override": False},
    {"name": "Effulgent Sun", "tier": "T2", "suits_roles": ["DPS Lead"], "suits_troops": ["SW", "CAV"], "priority_rank": "3", "wrong_for": "Tactical, Gathering, Siege", "ftp_rating": "Okay", "meta_override": False},
    {"name": "Messenger of Destruction", "tier": "T2", "suits_roles": ["DPS Lead"], "suits_troops": ["PIK"], "priority_rank": "1", "wrong_for": "Non-PIK, Gathering", "ftp_rating": "Must-have", "meta_override": False},
    {"name": "Ring of Falcon", "tier": "T1", "suits_roles": ["Healer Support", "Tank Support"], "suits_troops": ["Universal"], "priority_rank": "1", "wrong_for": "DPS Lead", "ftp_rating": "Must-have", "meta_override": False},
    {"name": "Scorching Flame", "tier": "T2", "suits_roles": ["Damage Support", "DPS Lead"], "suits_troops": ["CAV", "SW"], "priority_rank": "2", "wrong_for": "Gathering, Siege", "ftp_rating": "Okay", "meta_override": False},
    {"name": "Ring of Tulip", "tier": "T0", "suits_roles": ["DPS Lead", "Damage Support"], "suits_troops": ["SW", "PIK"], "priority_rank": "2", "wrong_for": "Gathering, Healer Support", "ftp_rating": "Great", "meta_override": False},
    {"name": "Ring of Rhino", "tier": "T1", "suits_roles": ["Siege"], "suits_troops": ["Universal"], "priority_rank": "1", "wrong_for": "All combat, Gathering", "ftp_rating": "Avoid", "meta_override": False},
    {"name": "Radiant Guardian", "tier": "T2", "suits_roles": ["DPS Lead"], "suits_troops": ["Universal"], "priority_rank": "1 — Lu Bu only", "wrong_for": "All non-Lu Bu heroes", "ftp_rating": "Meta Override", "meta_override": True},
    {"name": "Ring of Violet", "tier": "T0", "suits_roles": ["Gathering"], "suits_troops": ["GATH"], "priority_rank": "1", "wrong_for": "All combat", "ftp_rating": "Avoid", "meta_override": False},
    {"name": "Skyward Knight", "tier": "T2", "suits_roles": ["Damage Support", "Tank Support"], "suits_troops": ["SW", "ARC"], "priority_rank": "1", "wrong_for": "DPS Lead, Gathering", "ftp_rating": "Must-have", "meta_override": False},
    {"name": "Ring of Iris", "tier": "T0", "suits_roles": ["Universal"], "suits_troops": ["Universal"], "priority_rank": "4", "wrong_for": "Gathering, Siege", "ftp_rating": "Okay", "meta_override": False},
    {"name": "Lord of Eastern Heavens", "tier": "T2", "suits_roles": ["Universal"], "suits_troops": ["Universal"], "priority_rank": "—", "wrong_for": "All roles and troop types", "ftp_rating": "Ignore", "meta_override": False},
    {"name": "Ring of Sunflower", "tier": "T0", "suits_roles": ["Gathering"], "suits_troops": ["GATH"], "priority_rank": "2", "wrong_for": "All combat", "ftp_rating": "Avoid", "meta_override": False},
    {"name": "Ring of Boar", "tier": "T1", "suits_roles": ["Damage Support", "Tank Support"], "suits_troops": ["PIK"], "priority_rank": "1", "wrong_for": "DPS Lead, Gathering", "ftp_rating": "Must-have", "meta_override": False},
    {"name": "Ring of Seahorse", "tier": "T1", "suits_roles": ["Tank Support"], "suits_troops": ["Universal"], "priority_rank": "3", "wrong_for": "DPS Lead, Gathering", "ftp_rating": "Okay", "meta_override": False},
    {"name": "Ring of Steed", "tier": "T1", "suits_roles": ["Gathering"], "suits_troops": ["GATH"], "priority_rank": "1", "wrong_for": "All combat", "ftp_rating": "Must-have", "meta_override": False},
    {"name": "Ring of Bear", "tier": "T1", "suits_roles": ["DPS Lead", "Damage Support"], "suits_troops": ["CAV", "SW"], "priority_rank": "1", "wrong_for": "Healer Support, Gathering", "ftp_rating": "Great", "meta_override": False},
    {"name": "Ring of Rose", "tier": "T0", "suits_roles": ["Damage Support"], "suits_troops": ["SW", "ARC"], "priority_rank": "3", "wrong_for": "Warrior SW, Gathering", "ftp_rating": "Okay", "meta_override": False},
    {"name": "Ring of Serpent", "tier": "T1", "suits_roles": ["Damage Support"], "suits_troops": ["SW", "ARC"], "priority_rank": "1", "wrong_for": "Warrior SW, PIK, Gathering", "ftp_rating": "Great", "meta_override": False},
    {"name": "Ring of Badger", "tier": "T1", "suits_roles": ["Tank Support"], "suits_troops": ["PIK", "SW"], "priority_rank": "2", "wrong_for": "DPS Lead, Gathering", "ftp_rating": "Flexible", "meta_override": False},
    {"name": "Everflame Wings", "tier": "T2", "suits_roles": ["Damage Support"], "suits_troops": ["SW", "ARC"], "priority_rank": "1", "wrong_for": "Warrior SW, PIK, Gathering", "ftp_rating": "Must-have", "meta_override": False},
    {"name": "Ring of Deer", "tier": "T1", "suits_roles": ["Damage Support", "Tank Support"], "suits_troops": ["Universal"], "priority_rank": "2", "wrong_for": "Gathering, Siege", "ftp_rating": "Great", "meta_override": False},
    {"name": "Azure Moon", "tier": "T2", "suits_roles": ["Damage Support"], "suits_troops": ["SW", "ARC"], "priority_rank": "2", "wrong_for": "Warrior SW, PIK, CAV, Gathering", "ftp_rating": "Okay", "meta_override": False},
    {"name": "Ring of Clover", "tier": "T0", "suits_roles": ["Tank Support", "DPS Lead"], "suits_troops": ["Universal"], "priority_rank": "1", "wrong_for": "Gathering", "ftp_rating": "Must-have", "meta_override": False},
    {"name": "Sacred Sage", "tier": "T2", "suits_roles": ["Healer Support", "Tank Support"], "suits_troops": ["PIK"], "priority_rank": "1", "wrong_for": "Warrior formations, Gathering", "ftp_rating": "Must-have", "meta_override": False},
    {"name": "Tranquil Water", "tier": "T2", "suits_roles": ["Tank Support", "DPS Lead"], "suits_troops": ["Universal"], "priority_rank": "1", "wrong_for": "Gathering, Siege", "ftp_rating": "Must-have", "meta_override": False},
    {"name": "Ring of Lily", "tier": "T0", "suits_roles": ["Healer Support"], "suits_troops": ["Universal"], "priority_rank": "1", "wrong_for": "DPS Lead", "ftp_rating": "Okay", "meta_override": False},
    {"name": "Ring of Daisy", "tier": "T0", "suits_roles": ["DPS Lead"], "suits_troops": ["Universal"], "priority_rank": "1", "wrong_for": "Healer Support, Gathering", "ftp_rating": "Must-have", "meta_override": False},
    {"name": "Ring of Lion", "tier": "T1", "suits_roles": ["Universal"], "suits_troops": ["Universal"], "priority_rank": "3", "wrong_for": "Gathering, Siege", "ftp_rating": "Flexible", "meta_override": False},
    {"name": "Ring of Night Wolf", "tier": "T1", "suits_roles": ["DPS Lead"], "suits_troops": ["Universal"], "priority_rank": "1 — Lu Bu only", "wrong_for": "All non-Lu Bu heroes", "ftp_rating": "Meta Override", "meta_override": True},
    {"name": "Ring of Laurel", "tier": "T0", "suits_roles": ["Siege"], "suits_troops": ["Universal"], "priority_rank": "1", "wrong_for": "All combat, Gathering", "ftp_rating": "Avoid", "meta_override": False},
    {"name": "Ring of Crow", "tier": "T1", "suits_roles": ["Damage Support"], "suits_troops": ["SW"], "priority_rank": "2", "wrong_for": "Warrior SW, PIK, CAV, Gathering", "ftp_rating": "Flexible", "meta_override": False},
    {"name": "Ring of Elephant", "tier": "T1", "suits_roles": ["Siege"], "suits_troops": ["Universal"], "priority_rank": "2", "wrong_for": "All combat, Gathering", "ftp_rating": "Avoid", "meta_override": False},
    {"name": "Ring of Hyacinth", "tier": "T0", "suits_roles": ["Universal"], "suits_troops": ["Universal"], "priority_rank": "—", "wrong_for": "All combat roles", "ftp_rating": "Avoid", "meta_override": False},
]

RING_POOL_BY_NAME = {r["name"]: r for r in RING_POOL}
GATHERING_RING_NAMES = ["Ring of Steed", "Ring of Violet", "Ring of Sunflower"]
SIEGE_RING_NAMES = ["Ring of Rhino", "Ring of Elephant", "Ring of Laurel"]
META_OVERRIDE_HERO = "Lu Bu"
META_OVERRIDE_RING_NAMES = {"Ring of Night Wolf", "Radiant Guardian"}
COMBAT_PLACEHOLDER_RINGS = ["Ring of Iris", "Ring of Tulip", "Ring of Rose", "Ring of Lion"]
RING_TIER_ORDER = {"T2": 2, "T1": 1, "T0": 0}
MARCH_SLOT_LABELS = ["Lead", "Sup1", "Sup2"]


def _priority_rank_key(priority_rank: str) -> int:
    """Lower number = higher priority. Non-numeric ranks (e.g. '—') sort last."""
    match = re.match(r"^(\d+)", priority_rank or "")
    return int(match.group(1)) if match else 999


def _is_gathering_hero(hero: dict) -> bool:
    role = (hero.get("role") or "").strip().lower()
    troop = (hero.get("troop_type") or "").strip().upper()
    return role == "gathering" or troop == "gath"


def _is_siege_hero(hero: dict) -> bool:
    return (hero.get("role") or "").strip().lower() == "siege"


def _best_pool_match(hero: dict, pool: list[dict]) -> Optional[dict]:
    """Highest-tier ring in pool matching hero role + troop type, excluding
    Ignore-rated rings. Ties broken by lowest priority_rank number."""
    role = hero.get("role", "")
    troop = (hero.get("troop_type") or "").upper()
    candidates = [
        r for r in pool
        if role in r["suits_roles"]
        and (troop in r["suits_troops"] or "Universal" in r["suits_troops"])
        and r["ftp_rating"] != "Ignore"
    ]
    if not candidates:
        return None
    candidates.sort(key=lambda r: (-RING_TIER_ORDER.get(r.get("tier", ""), -1), _priority_rank_key(r["priority_rank"])))
    return candidates[0]


def _build_recommendation(hero: dict, chosen_ring: Optional[dict]) -> dict:
    equipped = (hero.get("ring") or "").strip()
    recommended = chosen_ring["name"] if chosen_ring else ""
    entry = {
        "march":       hero.get("march", ""),
        "slot":        hero.get("slot", ""),
        "hero":        hero.get("name", ""),
        "role":        hero.get("role", ""),
        "troop_type":  hero.get("troop_type", ""),
        "equipped":    equipped,
        "recommended": recommended,
    }
    if not equipped:
        entry["status"] = "missing"
        entry["note"] = "No ring equipped — equip anything from inventory now."
    elif equipped not in RING_POOL_BY_NAME:
        entry["status"] = "unrecognised"
        entry["note"] = "Ring not recognised in RING_POOL — verify in-game."
    elif equipped == recommended:
        entry["status"] = "match"
        entry["note"] = ""
    else:
        entry["status"] = "mismatch"
        entry["note"] = f"Replace with {recommended}." if recommended else "No suitable replacement found in pool."
    return entry


def resolve_ring_recommendations(marches: list[dict]) -> list[dict]:
    """Pool-based ring cascade allocation. Runs at profile-analysis query
    time -- never baked into hero records.

    Input: list of march dicts, each {"id": "M1", "heroes": [hero, ...]}
    with up to 3 heroes per march in Lead/Sup1/Sup2 order. Each hero dict
    has "name", "role", "troop_type", "ring" (currently equipped ring name
    or empty/None).

    Output: list of per-hero recommendation dicts (see _build_recommendation),
    in the same march/slot order they were submitted.
    """
    # 1. Full pool, 2/3. remove gathering and siege sub-pools from general circulation
    general_pool = [
        r for r in RING_POOL
        if r["name"] not in GATHERING_RING_NAMES and r["name"] not in SIEGE_RING_NAMES
    ]

    # 4. Meta overrides: reserve Night Wolf + Radiant Guardian for Lu Bu only
    has_meta_override_hero = any(
        h.get("name") == META_OVERRIDE_HERO
        for m in marches for h in m.get("heroes", [])
    )
    reserved_for_meta_hero = []
    if has_meta_override_hero:
        reserved_for_meta_hero = [r for r in general_pool if r["name"] in META_OVERRIDE_RING_NAMES]
    general_pool = [r for r in general_pool if r["name"] not in META_OVERRIDE_RING_NAMES]

    # Flatten into priority order: M1 Lead/Sup1/Sup2, M2 ..., M5 (combat only).
    # Gathering and siege heroes are routed to their own sub-pools (steps 7+).
    ordered_combat_heroes = []
    gathering_heroes = []
    siege_heroes = []
    for march in marches:
        march_id = march.get("id", "")
        for idx, hero in enumerate(march.get("heroes", [])[:3]):
            slot = MARCH_SLOT_LABELS[idx] if idx < len(MARCH_SLOT_LABELS) else f"Sup{idx}"
            entry = {**hero, "march": march_id, "slot": slot}
            if _is_gathering_hero(entry):
                gathering_heroes.append(entry)
            elif _is_siege_hero(entry):
                siege_heroes.append(entry)
            else:
                ordered_combat_heroes.append(entry)

    allocated = set()
    recommendations = []

    # 5/6. Main priority loop over combat heroes
    for hero in ordered_combat_heroes:
        if hero.get("name") == META_OVERRIDE_HERO and reserved_for_meta_hero:
            available_meta = [r for r in reserved_for_meta_hero if r["name"] not in allocated]
            available_meta.sort(key=lambda r: -RING_TIER_ORDER.get(r.get("tier", ""), -1))
            chosen = available_meta[0] if available_meta else None
        else:
            available = [r for r in general_pool if r["name"] not in allocated]
            chosen = _best_pool_match(hero, available)
            if chosen is None:
                for placeholder_name in COMBAT_PLACEHOLDER_RINGS:
                    if placeholder_name not in allocated and placeholder_name in RING_POOL_BY_NAME:
                        chosen = RING_POOL_BY_NAME[placeholder_name]
                        break
        if chosen:
            allocated.add(chosen["name"])
        recommendations.append(_build_recommendation(hero, chosen))

    # 7. Siege heroes: siege sub-pool only, by fixed priority Rhino > Elephant > Laurel
    for hero in siege_heroes:
        chosen = None
        for ring_name in SIEGE_RING_NAMES:
            if ring_name not in allocated and ring_name in RING_POOL_BY_NAME:
                chosen = RING_POOL_BY_NAME[ring_name]
                break
        if chosen:
            allocated.add(chosen["name"])
        recommendations.append(_build_recommendation(hero, chosen))

    # 7. GATH heroes: gathering sub-pool only, by fixed priority Steed > Violet > Sunflower
    for hero in gathering_heroes:
        chosen = None
        for ring_name in GATHERING_RING_NAMES:
            if ring_name not in allocated and ring_name in RING_POOL_BY_NAME:
                chosen = RING_POOL_BY_NAME[ring_name]
                break
        if chosen:
            allocated.add(chosen["name"])
        recommendations.append(_build_recommendation(hero, chosen))

    return recommendations


# ─── Session Store ────────────────────────────────────────────────────────────

sessions: dict[str, dict] = {}

def get_session(session_id: str) -> dict:
    now = datetime.utcnow()
    if session_id not in sessions:
        sessions[session_id] = {
            "history": [],
            "message_count": 0,
            "created": now,
            "last_active": now,
        }
    sessions[session_id]["last_active"] = now
    return sessions[session_id]


def prune_sessions():
    cutoff = datetime.utcnow() - timedelta(seconds=SESSION_TTL)
    expired = [sid for sid, s in sessions.items() if s["last_active"] < cutoff]
    for sid in expired:
        del sessions[sid]

# ─── Flask App ────────────────────────────────────────────────────────────────

app = Flask(__name__)
CORS(
    app,
    origins=ALLOWED_ORIGINS,
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
    supports_credentials=False,
    max_age=86400
)

anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


@app.after_request
def add_cors(response):
    """Belt-and-suspenders CORS — ensures headers on every response including OPTIONS."""
    origin = request.headers.get("Origin", "")
    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"]  = origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Max-Age"]       = "86400"
    return response

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/ping", methods=["GET", "OPTIONS"])
def ping():
    return jsonify({"pong": True})


@app.route("/")
def index():
    return send_from_directory(".", "AIGA_March_Analyser.html")


@app.route("/aiga")
def aiga_chat():
    return send_from_directory(".", "AIGA_Chat.html")


@app.route("/commander")
def commander():
    return send_from_directory(".", "AIGA_Commander.html")


@app.route("/analyse", methods=["POST"])
def analyse():
    try:
        data = request.get_json(silent=True) or {}
        message = str(data.get("message", "")).strip()
        marches = data.get("marches")

        # Run the deterministic ring cascade automatically whenever a
        # structured profile (marches) is submitted, so the model is grounded
        # in verified math rather than reasoning about RING_POOL freehand.
        ring_recommendations = []
        if isinstance(marches, list) and marches:
            ring_recommendations = resolve_ring_recommendations(marches)

        if not message and not ring_recommendations:
            return jsonify({"error": "Empty request"}), 400

        message = html.escape(message)[:MAX_INPUT_LEN]

        user_content = message
        if ring_recommendations:
            ring_section = (
                "VERIFIED RING ANALYSIS (computed server-side from RING_POOL "
                "cascade allocation -- use these exact statuses and replacements "
                "for the ring category, do not recompute or second-guess them):\n"
                + json.dumps(ring_recommendations, ensure_ascii=False)
            )
            user_content = f"{message}\n\n{ring_section}" if message else ring_section

        response = anthropic_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}]
        )
        return jsonify({
            "response": response.content[0].text,
            "ring_recommendations": ring_recommendations,
        })
    except Exception:
        return jsonify({"error": "Analysis failed. Please try again."}), 500


@app.route("/chat", methods=["POST"])
def chat():
    prune_sessions()

    try:
        data = request.get_json(silent=True) or {}
        raw_message = str(data.get("message", "")).strip()
        session_id  = str(data.get("session_id", "")).strip() or str(uuid.uuid4())
    except Exception:
        return jsonify({"error": "Invalid request."}), 400

    image_data = str(data.get("image", "")).strip()
    image_type = str(data.get("image_type", "image/jpeg")).strip()

    if not raw_message and not image_data:
        return jsonify({"error": "Empty message."}), 400
    message = html.escape(raw_message)[:MAX_INPUT_LEN] if raw_message else "Please analyse this screenshot."

    session = get_session(session_id)

    if session["message_count"] >= RATE_LIMIT:
        return jsonify({
            "error": "Daily limit reached. Come back tomorrow or upgrade to Commander tier.",
            "session_id": session_id,
        }), 429

    if image_data:
        user_content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": image_type,
                    "data": image_data,
                }
            },
            {"type": "text", "text": message}
        ]
    else:
        user_content = message

    history = list(session["history"])
    history.append({"role": "user", "content": user_content})

    try:
        response = anthropic_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            system=SYSTEM_PROMPT,
            messages=history
        )
        reply = response.content[0].text

        session["history"].append({"role": "user",      "content": user_content})
        session["history"].append({"role": "assistant", "content": reply})
        if len(session["history"]) > CONTEXT_TURNS * 2:
            session["history"] = session["history"][-(CONTEXT_TURNS * 2):]
        session["message_count"] += 1

        remaining = RATE_LIMIT - session["message_count"]
        return jsonify({
            "response":   reply,
            "session_id": session_id,
            "remaining":  remaining,
        })

    except anthropic.APIStatusError as e:
        if e.status_code == 529:
            print(f"[AIGA] Overloaded: {e}")
            remaining = RATE_LIMIT - session["message_count"]
            return jsonify({
                "response":   "The war council is overrun. Try again in a moment, Commander.",
                "session_id": session_id,
                "remaining":  remaining,
            }), 200
        print(f"[AIGA] API error: {e}")
        return jsonify({"error": "Could not reach AIGA. Please try again."}), 500
    except anthropic.APIError as e:
        print(f"[AIGA] API error: {e}")
        return jsonify({"error": "Could not reach AIGA. Please try again."}), 500
    except Exception as e:
        print(f"[AIGA] Unexpected error: {e}")
        return jsonify({"error": "Something went wrong. Please try again."}), 500


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
