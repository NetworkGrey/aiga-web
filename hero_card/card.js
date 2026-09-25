/*
 * AIGA hero card (UX Decisions v1.7). Landing, hero picker, the card with
 * 8 tap zones on the universal avatar, and one tap card per slot.
 *
 * Every mark comes from diff_rules.js (Diff Rules Spec v1.0); this file only
 * adapts card state and the generated reference data (card_data.js) into the
 * engine's inputs, and renders the result.
 */
(function () {
  "use strict";

  const R = window.AIGADiffRules;
  const STORE_KEY = "aiga_hero_card_v1";
  const AVATAR = "/static/hero-art/viking-female.jpg";
  const AVATAR_ALT = "Braided rider in scale armour on a white horse, original artwork";

  const TROOP_LABEL = { SW: "Sword", PIK: "Pike", CAV: "Cavalry", ARC: "Archer", GATH: "Gathering" };
  const TROOP_ORDER = ["CAV", "SW", "PIK", "ARC", "GATH"];
  const GEAR_SLOTS = ["Head", "Arms", "Chest", "Legs"];
  const SLOTS = ["Head", "Arms", "Chest", "Legs", "Ring", "Mount", "Adornment", "Skills"];

  // Marker centres on the universal avatar, measured on the 390x585 mock-up
  // frame and stored as percentages so they scale with the rendered image.
  // A second avatar needs its own measured set.
  const FRAME = { w: 390, h: 585 };
  const MARKERS = {
    Head: [180, 74], Chest: [185, 217], Arms: [99, 273], Ring: [95, 333],
    Skills: [217, 393], Legs: [116, 463], Mount: [333, 259], Adornment: [301, 500],
  };
  const FLIPPED_LABELS = new Set(["Mount", "Adornment"]);

  // Gem sockets per gear slot: Head takes Strategy, Arms Hero, Chest Tactic,
  // Legs one of each. The key names the hero's Meta Gem field for the socket.
  const GEM_SOCKETS = {
    Head:  [["Strategy", "head"], ["Strategy", "head"], ["Strategy", "head"]],
    Arms:  [["Hero", "arms"], ["Hero", "arms"], ["Hero", "arms"]],
    Chest: [["Tactic", "chest"], ["Tactic", "chest"], ["Tactic", "chest"]],
    Legs:  [["Strategy", "legs_strategy"], ["Hero", "legs_hero"], ["Tactic", "legs_tactic"]],
  };
  // Gem rarity only ever sets the diamond colour, never the mark.
  const GEM_RARITIES = [
    ["Common", "#9A9A9A"], ["Advanced", "#4CAF50"], ["Rare", "#4A90D9"],
    ["Epic", "#9B6BDB"], ["Legendary", "#D9A93E"], ["Mythical", "#E5484D"],
  ];
  const MOUNT_RARITIES = ["Courser (Common)", "Destrier (Epic)", "Skywing (Legendary)", "Celestial Charger (Mythical)"];
  const MOUNT_ATTRIBUTES = ["Might", "Strategy", "Armor", "Siege"];
  const ADORNMENT_FORMS = {
    SW: ["Swift Blade", "Mystic Mirror"], PIK: ["Guiding Star", "Stalwart Shield"],
    CAV: ["Unyielding Iron", "Sacred Lily"], ARC: ["Piercing Arrow", "Eagle's Blessing"],
  };
  const FORM_ORIENTATION = {};
  Object.values(ADORNMENT_FORMS).forEach(([attack, defense]) => {
    FORM_ORIENTATION[attack] = "Attack";
    FORM_ORIENTATION[defense] = "Defense";
  });

  // ── Reference data (card_data.js) mapped to the engine's shapes ────────────
  const byName = (rows, map) => Object.fromEntries(rows.map((r) => [r.name, map(r)]));
  const exclusions = (r) => ({
    excludedRoles: r.excluded_roles, excludedTroops: r.excluded_troops,
    excludedKits: r.excluded_kits, reservedClaimants: r.reserved_claimants, dataStatus: r.data_status,
  });
  const HERO_BY_NAME = byName(HERO_META, (h) => h);
  const RINGS = byName(RING_POOL, (r) => Object.assign({ name: r.name, tier: r.tier }, exclusions(r)));
  const TRAITS = byName(MOUNT_TRAITS, (t) => Object.assign({
    name: t.name, attribute: t.attribute, requiresAttributeMatch: t.requires_attribute_match,
  }, exclusions(t)));
  const EFFECTS = byName(ADORNMENT_EFFECTS, (e) => Object.assign({ name: e.name, troopType: e.troop_type }, exclusions(e)));
  const GEMS = byName(GEM_TYPES, (g) => ({
    name: g.name, category: g.category, isPlaceholder: g.is_placeholder,
    placeholderFor: g.placeholder_for, dataStatus: g.data_status,
  }));
  const GEAR = byName(GEAR_PIECES, (p) => ({
    name: p.name, troopType: p.troop_type, slot: p.slot, rarity: p.rarity, maxLevel: p.max_level, dataStatus: p.data_status,
  }));
  const ALL_SKILLS = [...new Set(HERO_META.flatMap((h) =>
    h.skills.concat([h.skill3_rec], h.skill4_recs, h.skill3_alternates, h.skill4_alternates)).filter(Boolean))].sort();

  // ── Helpers ─────────────────────────────────────────────────────────────────
  const esc = (v) => String(v == null ? "" : v).replace(/[&<>"']/g, (c) => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const troopsOf = (meta) => [...new Set((meta.type || "").split("/").filter(Boolean))];
  const initials = (name) => {
    const words = name.split(/\s+/).filter((w) => /^[A-Z]/.test(w));
    return words.length > 1 ? words[0][0] + words[1][0] : name.slice(0, 2).toUpperCase();
  };
  const clamp = (n, lo, hi) => Math.min(hi, Math.max(lo, n));

  const MARK_ICON = {
    green: (s) => `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12l5 5 9-10"/></svg>`,
    orange: (s) => `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" aria-hidden="true"><path d="M12 5v8.5"/><path d="M12 18.5h.01"/></svg>`,
    red: (s) => `<svg width="${s - 1}" height="${s - 1}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12"/><path d="M18 6L6 18"/></svg>`,
    grey: (s) => `<span aria-hidden="true" style="font-size:${s + 1}px">?</span>`,
    none: (s) => `<span aria-hidden="true" style="font-size:${s}px">–</span>`,
  };
  const MARK_WORDS = {
    green: "meta correct", orange: "better option available", red: "wrong, change it",
    grey: "no verified meta", none: "not filled in yet",
  };
  function markBadge(mark, size) {
    const m = mark || "none";
    const box = size + 4;
    return `<span class="mark ${m}" style="width:${box}px;height:${box}px">${MARK_ICON[m](Math.round(size * 0.46))}</span>`;
  }

  // ── State (browser storage; the card must still render without it) ───────
  function emptyEquipped() {
    const gear = {};
    GEAR_SLOTS.forEach((slot) => {
      gear[slot] = { piece: "", level: 0, stars: 0, gems: [0, 1, 2].map(() => ({ type: "", rarity: "" })) };
    });
    return {
      playAs: "",
      gear,
      ring: { name: "", level: 0 },
      mount: { trait: "", trait2: "", attributes: [], rarity: "" },
      adornment: { form: "", effect: "", level: 0 },
      skills: { s3: "", s4: "", l1: 0, l2: 0, l3: 0, l4: 0 },
      // Slots the player has saved or edited. An untouched slot hasn't been
      // filled in yet, which is not the same as an empty slot, so it carries
      // no mark rather than a red "equip anything".
      touched: {},
    };
  }
  function loadState() {
    try {
      const saved = JSON.parse(localStorage.getItem(STORE_KEY) || "null");
      if (saved && saved.heroes) return Object.assign({ view: "landing", hero: "", open: "", filter: "All", query: "" }, saved);
    } catch (e) { /* storage unavailable or corrupt: start fresh */ }
    return { view: "landing", hero: "", open: "", filter: "All", query: "", heroes: {} };
  }
  function saveState() {
    try { localStorage.setItem(STORE_KEY, JSON.stringify(state)); } catch (e) { /* non-fatal */ }
  }
  let state = loadState();
  const equippedFor = (name) => state.heroes[name] || (state.heroes[name] = emptyEquipped());

  // ── Engine adapters ─────────────────────────────────────────────────────────
  function engineHero(meta) {
    return {
      name: meta.name,
      troops: troopsOf(meta),
      cardRole: meta.card_role,
      damageKit: meta.damage_kit,
      ring: { T0: meta.ring_t0, T1: meta.ring_t1, T2: meta.ring_t2 },
      mount: { traits: meta.mount_traits },
      adornment: { effects: meta.adornment_effects },
    };
  }
  // A dual hero's current side comes from the "Play as" toggle.
  function context(meta, eq) {
    const troops = troopsOf(meta);
    return { marchTroop: troops.length > 1 ? eq.playAs : troops[0] };
  }
  // Every hero with a saved card counts as the roster for move prompts.
  function roster() {
    return Object.entries(state.heroes).map(([name, eq]) => ({
      name, ring: eq.ring.name,
      mountTraits: [eq.mount.trait, eq.mount.trait2].filter(Boolean),
      adornmentEffect: eq.adornment.effect,
    }));
  }

  function evaluate(meta, eq) {
    const hero = engineHero(meta);
    const ctx = context(meta, eq);
    const team = roster();
    const out = {};

    GEAR_SLOTS.forEach((slot) => {
      const g = eq.gear[slot];
      const pieceRecord = GEAR[g.piece];
      const piece = R.evaluateGearPiece({
        hero, context: ctx,
        equipped: pieceRecord && { troopType: pieceRecord.troopType, rarity: pieceRecord.rarity, dataStatus: pieceRecord.dataStatus },
      });
      const gems = GEM_SOCKETS[slot].map(([, key], i) => R.evaluateGem({
        hero, equipped: g.gems[i].type, target: meta.meta_gems[key],
        gearLevel: g.level, socketIndex: i, gemTypes: GEMS,
      }));
      out[slot] = { mark: R.gearSlotMarker(piece, gems), piece, gems };
    });

    out.Ring = R.evaluateRing({ hero, equipped: eq.ring.name, rings: RINGS, roster: team, context: ctx });
    out.Mount = R.evaluateMount({
      hero, traits: TRAITS, roster: team, context: ctx,
      equipped: { traits: [eq.mount.trait, eq.mount.trait2].filter(Boolean), attributes: eq.mount.attributes },
    });

    const form = R.evaluateAdornmentForm({ hero, equipped: eq.adornment.form, context: ctx });
    const effect = R.evaluateAdornmentEffect({ hero, equipped: eq.adornment.effect, effects: EFFECTS, roster: team, context: ctx });
    out.Adornment = { mark: R.worstMark([form, effect]), form, effect };

    const skills = [
      R.evaluateFixedSkill({ equipped: meta.skill1, meta: meta.skill1 }),
      R.evaluateFixedSkill({ equipped: meta.skill2, meta: meta.skill2 }),
      R.evaluateFlexSkill({ equipped: eq.skills.s3, meta: meta.skill3_rec, alternates: meta.skill3_alternates }),
      R.evaluateFlexSkill({ equipped: eq.skills.s4, meta: meta.skill4_recs, alternates: meta.skill4_alternates }),
    ];
    out.Skills = { mark: R.worstMark(skills), skills };

    SLOTS.forEach((slot) => {
      out[slot].mark = (eq.touched && eq.touched[slot] && out[slot].mark) || "none";
    });
    return out;
  }

  // ── Views ───────────────────────────────────────────────────────────────────
  const app = document.getElementById("app");

  const DISCLAIMER = "AIGA™ is an independent fan advisory service created by Network Grey (Pty) Ltd. Not affiliated with, endorsed by, or associated with TiMi Studio Group, Level Infinite, Proxima Beta Pte. Limited, Microsoft Corporation, or Xbox Game Studios. Age of Empires and Age of Empires Mobile are trademarks of Microsoft Corporation. All game content and imagery are the intellectual property of their respective owners. All data sources and community contributors are acknowledged where applicable. AIGA may make mistakes. Always verify information before acting on it.";

  function renderLanding() {
    return `<section class="landing">
      <header>
        <h1>AIGA</h1>
        <span class="tagline">Your AI Strategic Advisor</span>
        <p class="intro">Your AI-powered strategic advisor for hero builds, march formations, event strategy, and resource planning. Ask anything about your account.</p>
      </header>
      <div class="rule"></div>
      <div class="avatar"><img src="${AVATAR}" alt="${AVATAR_ALT}"></div>
      <button class="btn-primary" data-action="continue">Continue</button>
      <p class="disclaimer">${esc(DISCLAIMER)}</p>
    </section>`;
  }

  function matchesFilter(meta) {
    const troops = troopsOf(meta);
    const f = state.filter;
    if (f === "Dual" && troops.length < 2) return false;
    if (f !== "All" && f !== "Dual" && !troops.includes(f)) return false;
    return !state.query || meta.name.toLowerCase().includes(state.query.toLowerCase());
  }

  function renderPicker() {
    const chips = [["All", "All"], ["SW", "Sword"], ["PIK", "Pike"], ["CAV", "Cav"], ["ARC", "Archer"], ["Dual", "Dual"]];
    const groups = {};
    HERO_META.filter(matchesFilter).forEach((meta) => {
      const primary = troopsOf(meta)[0] || "Other";
      (groups[primary] = groups[primary] || []).push(meta);
    });
    const order = TROOP_ORDER.filter((t) => groups[t]).concat(Object.keys(groups).filter((t) => !TROOP_ORDER.includes(t)));
    const list = order.map((t) => `
      <div class="group-label">${esc((TROOP_LABEL[t] || t).toUpperCase())}</div>
      ${groups[t].slice().sort((a, b) => a.name.localeCompare(b.name)).map((meta) => {
        const troops = troopsOf(meta);
        const saved = state.heroes[meta.name] ? " saved" : "";
        return `<button class="hero-row${saved}" data-action="open-hero" data-hero="${esc(meta.name)}">
          <span class="initials" aria-hidden="true">${esc(initials(meta.name))}</span>
          <span class="name">${esc(meta.name)}</span>
          <span class="type-badge${troops.length > 1 ? " dual" : ""}">${esc(troops.join(" / ") || "—")}</span>
        </button>`;
      }).join("")}`).join("");

    return `<section class="picker">
      <div><div class="brand">AIGA</div><h1>Choose a hero</h1></div>
      <div class="import-soon" aria-disabled="true">
        <span class="icon" aria-hidden="true"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 16V4"/><path d="M7 9l5-5 5 5"/><path d="M4 20h16"/></svg></span>
        <span><strong>Upload hero screenshot <span class="soon">SOON</span></strong><span>For now, pick a hero and fill in manually</span></span>
      </div>
      <label class="search">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#A3A9B5" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>
        <span class="sr-only">Search heroes</span>
        <input type="search" data-input="query" value="${esc(state.query)}" placeholder="Search ${HERO_META.length} heroes">
      </label>
      <div class="chips" role="group" aria-label="Filter by troop type">
        ${chips.map(([v, label]) => `<button class="chip" data-action="filter" data-value="${v}" aria-pressed="${state.filter === v}">${label}</button>`).join("")}
      </div>
      <div>${list || '<p class="empty-state">No heroes match.</p>'}</div>
      <p class="disclaimer">Independent fan advisory tool by Network Grey. Not affiliated with or endorsed by TiMi Studio Group, Level Infinite, Proxima Beta, Microsoft or Xbox Game Studios.</p>
    </section>`;
  }

  function renderCard() {
    const meta = HERO_BY_NAME[state.hero];
    const eq = equippedFor(meta.name);
    const results = evaluate(meta, eq);
    const troops = troopsOf(meta);

    const markers = SLOTS.map((slot) => {
      const [x, y] = MARKERS[slot];
      const mark = results[slot].mark;
      const flip = FLIPPED_LABELS.has(slot) ? " flip" : "";
      const active = state.open === slot ? " active" : "";
      return `<button class="marker${flip}${active}" style="left:${(x / FRAME.w * 100).toFixed(2)}%;top:${(y / FRAME.h * 100).toFixed(2)}%"
        data-action="open-slot" data-slot="${slot}" aria-label="${slot}: ${MARK_WORDS[mark]}">
        <span class="hit">${markBadge(mark, 22)}</span><span class="label">${slot}</span>
      </button>`;
    }).join("");

    const counts = { green: 0, orange: 0, red: 0, grey: 0 };
    SLOTS.forEach((slot) => { if (counts[results[slot].mark] !== undefined) counts[results[slot].mark] += 1; });

    const playAs = troops.length > 1 ? `
      <div class="segmented" role="radiogroup" aria-label="Play as">
        ${troops.map((t) => `<button role="radio" aria-checked="${eq.playAs === t}" data-action="play-as" data-value="${t}">${esc(TROOP_LABEL[t] || t)}</button>`).join("")}
      </div>
      ${eq.playAs ? "" : '<p class="hint">Dual troop type: choose the side you play to judge troop-specific slots.</p>'}` : "";

    return `<section class="card">
      <div class="art">
        <img src="${AVATAR}" alt="${AVATAR_ALT}">
        <div class="card-top"><button class="back" data-action="back">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>Heroes</button></div>
        ${markers}
      </div>
      <div class="hero-title">
        <h1>${esc(meta.name)}</h1>
        <span class="type-badge">${esc(troops.join(" / ") || "—")}</span>
      </div>
      <div class="card-body">
        ${playAs}
        <div class="counts" aria-label="Slot summary">
          <span class="count green" aria-label="${counts.green} meta correct">${MARK_ICON.green(14)}${counts.green}</span>
          <span class="count orange" aria-label="${counts.orange} better option available">${MARK_ICON.orange(14)}${counts.orange}</span>
          <span class="count red" aria-label="${counts.red} wrong">${MARK_ICON.red(14)}${counts.red}</span>
          <span class="count grey" aria-label="${counts.grey} no verified meta">?<span>${counts.grey}</span></span>
        </div>
        <div class="card-actions">
          <button class="locked" disabled aria-disabled="true">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>
            Add to march <span class="soon">SOON</span></button>
          <button class="screenshot" disabled aria-disabled="true">Screenshot <span class="soon">SOON</span></button>
        </div>
      </div>
      ${state.open ? renderSheet(meta, eq, results) : ""}
    </section>`;
  }

  // ── Tap cards ───────────────────────────────────────────────────────────────
  function compareRow(tag, mark, title, detail) {
    return `<div class="compare-row ${mark}">
      <span class="tag">${tag}</span>
      <span class="what"><strong>${esc(title || "Empty")}</strong>${detail ? `<span>${esc(detail)}</span>` : ""}</span>
      ${markBadge(mark, 18)}
    </div>`;
  }

  function stepper(label, path, value, min, max) {
    return `<div class="stepper"><span>${label}</span><span class="ctl">
      <button data-action="step" data-path="${path}" data-delta="-1" data-min="${min}" data-max="${max}" aria-label="Decrease ${label.toLowerCase()}">−</button>
      <output aria-live="polite">${value}</output>
      <button data-action="step" data-path="${path}" data-delta="1" data-min="${min}" data-max="${max}" aria-label="Increase ${label.toLowerCase()}">+</button>
    </span></div>`;
  }

  function select(label, path, value, options, placeholder) {
    const opts = options.map((o) => {
      const [v, text] = Array.isArray(o) ? o : [o, o];
      return `<option value="${esc(v)}"${v === value ? " selected" : ""}>${esc(text)}</option>`;
    }).join("");
    return `<label class="field"><span>${label}</span><select data-path="${path}">
      <option value="">${esc(placeholder || "None")}</option>${opts}</select></label>`;
  }

  function adviceFor(result) {
    if (!result || !result.message) return "";
    return `<p class="advice">${esc(result.message)}</p>`;
  }

  function gearSheet(slot, meta, eq, res) {
    const g = eq.gear[slot];
    const piece = GEAR[g.piece];
    const troop = context(meta, eq).marchTroop;
    const pieces = GEAR_PIECES.filter((p) => p.slot === slot)
      .sort((a, b) => (a.troop_type !== troop) - (b.troop_type !== troop) || a.troop_type.localeCompare(b.troop_type));
    const maxLevel = piece ? piece.maxLevel : 80;
    const gems = GEM_SOCKETS[slot].map(([category, key], i) => {
      const gem = g.gems[i];
      const r = res.gems[i];
      const rarityColor = (GEM_RARITIES.find(([n]) => n === gem.rarity) || [])[1] || "#3A3F4B";
      const diamond = `<span class="diamond" style="background:${rarityColor}" title="${esc(gem.rarity || "No rarity")}"></span>`;
      if (r.mark === null) {
        return `<div class="gem-row">${diamond}<span class="locked-note">${esc(category)} socket · ${esc(r.message)}</span>${markBadge("none", 16)}</div>`;
      }
      const typeOptions = GEM_TYPES.filter((t) => t.category === category).map((t) => t.name);
      return `<div class="gem-row">${diamond}
        <select data-path="gear.${slot}.gems.${i}.type" aria-label="${category} gem ${i + 1} type">
          <option value="">${category} gem…</option>
          ${typeOptions.map((t) => `<option${t === gem.type ? " selected" : ""}>${esc(t)}</option>`).join("")}
        </select>
        <select data-path="gear.${slot}.gems.${i}.rarity" aria-label="${category} gem ${i + 1} rarity">
          <option value="">Rarity…</option>
          ${GEM_RARITIES.map(([n]) => `<option${n === gem.rarity ? " selected" : ""}>${n}</option>`).join("")}
        </select>
        ${markBadge(r.mark, 16)}</div>`;
    }).join("");

    return `
      <div class="compare">
        ${compareRow("YOURS", res.piece.mark, g.piece, piece ? `${piece.rarity} · ${TROOP_LABEL[piece.troopType]} · Lv${g.level} · ★${g.stars}` : "")}
      </div>
      ${adviceFor(res.piece)}
      <div class="fields">
        <span class="section-label">EDIT YOURS</span>
        ${select("Piece", `gear.${slot}.piece`, g.piece,
          pieces.map((p) => [p.name, `${p.name} (${TROOP_LABEL[p.troop_type]}, ${p.rarity})`]), "Nothing equipped")}
        <div class="grid-2">${stepper("Lv", `gear.${slot}.level`, g.level, 0, maxLevel)}${stepper("Stars", `gear.${slot}.stars`, g.stars, 0, 5)}</div>
        <div class="field"><span>Gems</span><div class="gem-list">${gems}</div></div>
      </div>`;
  }

  function ringSheet(meta, eq, res) {
    const path = ["T0", "T1", "T2"].filter((t) => meta["ring_" + t.toLowerCase()]).map((t) => `${t} ${meta["ring_" + t.toLowerCase()]}`);
    const taken = new Set(roster().filter((r) => r.name !== meta.name).map((r) => r.ring).filter(Boolean));
    const options = RING_POOL.slice().sort((a, b) => a.tier.localeCompare(b.tier) || a.name.localeCompare(b.name))
      .map((r) => [r.name, `${r.name} · ${r.tier}${taken.has(r.name) ? " (on another hero)" : ""}`]);
    return `
      <div class="compare">
        ${compareRow("YOURS", res.mark, eq.ring.name, eq.ring.name ? `${RINGS[eq.ring.name] ? RINGS[eq.ring.name].tier : "Unknown"} · Lv${eq.ring.level}` : "")}
        ${path.length ? compareRow("PATH", "none", path.join(" → "), "") : ""}
      </div>
      ${adviceFor(res)}
      <div class="fields">
        <span class="section-label">EDIT YOURS</span>
        ${select("Ring", "ring.name", eq.ring.name, options, "No ring equipped")}
        ${stepper("Lv", "ring.level", eq.ring.level, 0, 50)}
        <p class="note">One ring per hero, one copy per account.</p>
      </div>`;
  }

  function mountSheet(meta, eq, res) {
    const traits = MOUNT_TRAITS.map((t) => t.name);
    const wanted = meta.mount_traits.length ? meta.mount_traits.join(" + ") : "";
    return `
      <div class="compare">
        ${compareRow("YOURS", res.mark, [eq.mount.trait, eq.mount.trait2].filter(Boolean).join(" + "),
          [eq.mount.attributes.join(" / "), eq.mount.rarity].filter(Boolean).join(" · "))}
        ${wanted && res.mark !== "green" ? compareRow("META", "none", wanted, "") : ""}
      </div>
      ${adviceFor(res)}
      <div class="fields">
        <span class="section-label">EDIT YOURS</span>
        <div class="grid-2">${select("Trait", "mount.trait", eq.mount.trait, traits)}${select("Second trait", "mount.trait2", eq.mount.trait2, traits)}</div>
        <div class="field"><span>Attributes</span><div class="check-chips">
          ${MOUNT_ATTRIBUTES.map((a) => `<label><input type="checkbox" data-path="mount.attributes" value="${a}"${eq.mount.attributes.includes(a) ? " checked" : ""}>${a}</label>`).join("")}
        </div></div>
        ${select("Rarity", "mount.rarity", eq.mount.rarity, MOUNT_RARITIES, "Not set")}
        <p class="note">Temperament isn't asked for: once a mount is equipped it has no effect. Only the trait and attribute matter.</p>
      </div>`;
  }

  function adornmentSheet(meta, eq, res) {
    const troop = context(meta, eq).marchTroop;
    const forms = ADORNMENT_FORMS[troop] ? ADORNMENT_FORMS[troop] : [].concat(...Object.values(ADORNMENT_FORMS));
    const effects = ADORNMENT_EFFECTS.filter((e) => e.troop_type === "Universal" || !ADORNMENT_FORMS[troop] || e.troop_type === troop)
      .map((e) => [e.name, e.troop_type === "Universal" ? `${e.name} (all troops)` : e.name]);
    return `
      <div class="compare">
        ${compareRow("FORM", res.form.mark, eq.adornment.form, eq.adornment.form ? `${FORM_ORIENTATION[eq.adornment.form]} · Lv${eq.adornment.level}` : "")}
        ${compareRow("EFFECT", res.effect.mark, eq.adornment.effect, "")}
      </div>
      ${adviceFor(res.form)}${res.effect.message !== res.form.message ? adviceFor(res.effect) : ""}
      <div class="fields">
        <span class="section-label">EDIT YOURS</span>
        ${select("Form", "adornment.form", eq.adornment.form, forms.map((f) => [f, `${f} (${FORM_ORIENTATION[f]})`]), "No adornment")}
        ${select("Special effect", "adornment.effect", eq.adornment.effect, effects, "No effect")}
        ${stepper("Lv", "adornment.level", eq.adornment.level, 0, 60)}
      </div>`;
  }

  function skillsSheet(meta, eq, res) {
    const [s1, s2, s3, s4] = res.skills;
    const flexOptions = (rec) => [...new Set(meta.skills.concat(rec, ALL_SKILLS))].filter(Boolean);
    const fixed = (label, name, r, path, level) => `<div class="skill-row">
      <div class="field"><span>${label}</span><div class="fixed">${esc(name || "Not recorded")}${markBadge(r.mark, 16)}</div></div>
      ${stepper("Lv", path, level, 0, 40)}</div>`;
    const flex = (label, path, value, r, rec, lpath, level) => `<div class="skill-row">
      <div>${select(label, path, value, flexOptions(rec), "Not learned")}</div>
      ${stepper("Lv", lpath, level, 0, 40)}</div>
      ${r.mark === "green" ? "" : adviceFor(r)}`;
    return `
      <div class="compare">
        ${compareRow("CMDR", s1.mark, meta.skill1, "")}
        ${compareRow("SIG", s2.mark, meta.skill2, "")}
        ${compareRow("SKILL 3", s3.mark, eq.skills.s3, meta.skill3_rec ? `Meta: ${meta.skill3_rec}` : "")}
        ${compareRow("SKILL 4", s4.mark, eq.skills.s4, meta.skill4_recs.length ? `Meta: ${meta.skill4_recs.join(" or ")}` : "")}
      </div>
      <div class="fields">
        <span class="section-label">EDIT YOURS</span>
        ${fixed("Commander", meta.skill1, s1, "skills.l1", eq.skills.l1)}
        ${fixed("Signature", meta.skill2, s2, "skills.l2", eq.skills.l2)}
        ${flex("Skill 3", "skills.s3", eq.skills.s3, s3, [meta.skill3_rec], "skills.l3", eq.skills.l3)}
        ${flex("Skill 4", "skills.s4", eq.skills.s4, s4, meta.skill4_recs, "skills.l4", eq.skills.l4)}
      </div>`;
  }

  function renderSheet(meta, eq, results) {
    const slot = state.open;
    const res = results[slot];
    const troop = context(meta, eq).marchTroop;
    const body = GEAR_SLOTS.includes(slot) ? gearSheet(slot, meta, eq, res)
      : slot === "Ring" ? ringSheet(meta, eq, res)
      : slot === "Mount" ? mountSheet(meta, eq, res)
      : slot === "Adornment" ? adornmentSheet(meta, eq, res)
      : skillsSheet(meta, eq, res);
    const next = SLOTS[(SLOTS.indexOf(slot) + 1) % SLOTS.length];
    return `<div class="scrim" data-action="close"></div>
      <div class="sheet" role="dialog" aria-modal="true" aria-labelledby="sheet-title">
        <div class="grabber" aria-hidden="true"></div>
        <div class="sheet-head">
          ${markBadge(res.mark, 40)}
          <span class="titles"><h2 id="sheet-title">${slot}</h2><span class="sub">${esc(meta.name)}${troop ? " · " + esc(TROOP_LABEL[troop] || troop) : ""}</span></span>
          <button class="icon-btn" data-action="close" aria-label="Close">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12"/><path d="M18 6L6 18"/></svg></button>
        </div>
        ${body}
        <div class="sheet-actions">
          <button class="btn-secondary" data-action="open-slot" data-review="1" data-slot="${next}">Next: ${next}</button>
          <button class="btn-primary" data-action="close" data-review="1">Save</button>
        </div>
      </div>`;
  }

  // ── Render + events ─────────────────────────────────────────────────────────
  function render() {
    if (state.view === "card" && !HERO_BY_NAME[state.hero]) state.view = "picker";
    app.innerHTML = state.view === "landing" ? renderLanding()
      : state.view === "picker" ? renderPicker() : renderCard();
    const sheet = app.querySelector(".sheet");
    if (sheet && document.activeElement === document.body) sheet.querySelector("button, select, input").focus({ preventScroll: true });
  }

  function slotOfPath(path) {
    const [root, sub] = path.split(".");
    return root === "gear" ? sub : root.charAt(0).toUpperCase() + root.slice(1);
  }
  function touch(eq, slot) {
    if (!SLOTS.includes(slot)) return;
    eq.touched = eq.touched || {};
    eq.touched[slot] = true;
  }

  function setPath(obj, path, value) {
    const keys = path.split(".");
    const last = keys.pop();
    const target = keys.reduce((o, k) => o[k], obj);
    target[last] = value;
  }
  function getPath(obj, path) {
    return path.split(".").reduce((o, k) => o[k], obj);
  }

  app.addEventListener("click", (e) => {
    const el = e.target.closest("[data-action]");
    if (!el || el.disabled) return;
    const { action } = el.dataset;
    if (action === "continue") { state.view = "picker"; }
    else if (action === "filter") { state.filter = el.dataset.value; }
    else if (action === "open-hero") { state.hero = el.dataset.hero; state.view = "card"; state.open = ""; equippedFor(state.hero); window.scrollTo(0, 0); }
    else if (action === "back") { state.view = "picker"; state.open = ""; }
    else if (action === "open-slot") {
      if (el.dataset.review && state.open) touch(equippedFor(state.hero), state.open);
      state.open = el.dataset.slot;
    }
    else if (action === "close") {
      if (el.dataset.review && state.open) touch(equippedFor(state.hero), state.open);
      state.open = "";
    }
    else if (action === "play-as") { equippedFor(state.hero).playAs = el.dataset.value; }
    else if (action === "step") {
      const eq = equippedFor(state.hero);
      const next = clamp((Number(getPath(eq, el.dataset.path)) || 0) + Number(el.dataset.delta), Number(el.dataset.min), Number(el.dataset.max));
      setPath(eq, el.dataset.path, next);
      touch(eq, slotOfPath(el.dataset.path));
    } else return;
    saveState();
    render();
  });

  app.addEventListener("change", (e) => {
    const el = e.target;
    if (!el.dataset.path || !state.hero) return;
    const eq = equippedFor(state.hero);
    touch(eq, slotOfPath(el.dataset.path));
    if (el.type === "checkbox") {
      const list = getPath(eq, el.dataset.path);
      setPath(eq, el.dataset.path, el.checked ? list.concat(el.value) : list.filter((v) => v !== el.value));
    } else {
      setPath(eq, el.dataset.path, el.value);
      // A new gear piece can lower the level cap; keep the level within it.
      const gearMatch = el.dataset.path.match(/^gear\.(\w+)\.piece$/);
      if (gearMatch && GEAR[el.value]) {
        const g = eq.gear[gearMatch[1]];
        g.level = Math.min(g.level, GEAR[el.value].maxLevel);
      }
    }
    saveState();
    render();
  });

  app.addEventListener("input", (e) => {
    if (e.target.dataset.input !== "query") return;
    state.query = e.target.value;
    saveState();
    const caret = e.target.selectionStart;
    render();
    const box = app.querySelector('[data-input="query"]');
    box.focus();
    box.setSelectionRange(caret, caret);
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && state.open) { state.open = ""; saveState(); render(); }
  });

  render();
})();
