/*
 * AIGA hero card diff rules — implements AIGA_Diff_Rules_Spec_v1.md v1.0.
 *
 * Pure functions, no DOM. Every mark is derived here at card-build time from
 * reference records (rings, mount traits, adornment effects, gem types, gear
 * pieces) plus the hero's own meta. No verdict is ever stored.
 *
 * Every evaluate* function returns:
 *   { mark: "green"|"orange"|"red"|"grey"|null, step, message, ...extras }
 * `step` is the ladder step that matched (1-8), or a named rule for the
 * per-slot rules that sit outside the ladder ("skills-fixed", "locked").
 * mark === null only for a locked gem socket, which carries no mark at all.
 *
 * Runs in the browser (window.AIGADiffRules) and in Node (module.exports).
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.AIGADiffRules = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  const MARK = { GREEN: "green", ORANGE: "orange", RED: "red", GREY: "grey" };

  // Data contract: a record whose Data Status reads one of these must not
  // drive a confident green or red. Community sourced is not on the list.
  const UNVERIFIED_STATUSES = ["Needs in-game check", "Not gathered"];

  const TIER_ORDER = ["T0", "T1", "T2"];
  const COMBAT_TROOPS = ["SW", "PIK", "CAV", "ARC"];

  // Gem sockets unlock at gear level 10, 30 and 60 on every gear slot.
  const GEM_SOCKET_UNLOCK = [10, 30, 60];

  // Adornment forms per troop type. Orientation is a fixed property of the
  // form name and is never stored separately.
  const ADORNMENT_FORMS = {
    SW:  { Attack: "Swift Blade",     Defense: "Mystic Mirror" },
    PIK: { Attack: "Guiding Star",    Defense: "Stalwart Shield" },
    CAV: { Attack: "Unyielding Iron", Defense: "Sacred Lily" },
    ARC: { Attack: "Piercing Arrow",  Defense: "Eagle's Blessing" },
  };

  const WORST_ORDER = [MARK.RED, MARK.ORANGE, MARK.GREY, MARK.GREEN];

  // ── Helpers ────────────────────────────────────────────────────────────────

  function result(mark, step, message, extras) {
    return Object.assign({ mark, step, message }, extras || {});
  }

  function isUnverified(record) {
    return !!record && UNVERIFIED_STATUSES.includes(record.dataStatus);
  }

  function list(value) {
    if (!value) return [];
    return Array.isArray(value) ? value : [value];
  }

  function heroTroops(hero) {
    return list(hero.troops);
  }

  function isDualHero(hero) {
    return heroTroops(hero).length > 1;
  }

  // The troop type the hero is fighting as right now. Single-type heroes know
  // it statically; dual heroes only know it from their current march.
  function currentTroop(hero, context) {
    const troops = heroTroops(hero);
    if (context && context.marchTroop && troops.includes(context.marchTroop)) {
      return context.marchTroop;
    }
    return troops.length === 1 ? troops[0] : null;
  }

  function isGatheringHero(hero) {
    return hero.cardRole === "Gathering" || heroTroops(hero).includes("GATH");
  }

  function hasSpecificTroopExclusion(item) {
    return list(item.excludedTroops).some((t) => t !== "Universal");
  }

  // Ladder step 2: the exclusion cannot be evaluated without the hero's kit.
  // Role and troop are always needed; the damage kit only when the item
  // actually excludes by kit.
  function cannotEvaluateExclusion(hero, item, context) {
    if (!hero.cardRole) return "Hero role not recorded";
    if (!currentTroop(hero, context)) {
      return isDualHero(hero)
        ? "Dual troop type: current march troop type not known"
        : "Hero troop type not recorded";
    }
    if (item && list(item.excludedKits).length && !hero.damageKit) {
      return "Hero damage kit not recorded";
    }
    return null;
  }

  // Ladder step 3: Excluded For (functional). "Universal" in an excluded list
  // means every value.
  function exclusionReason(hero, item, context) {
    if (!item) return null;
    const roles = list(item.excludedRoles);
    if (roles.includes("Universal") || roles.includes(hero.cardRole)) {
      return `Does not work on a ${hero.cardRole}`;
    }
    const troops = list(item.excludedTroops);
    const troop = currentTroop(hero, context);
    if (troops.includes("Universal") || troops.includes(troop)) {
      return `Does not work on ${troop} troops`;
    }
    if (hero.damageKit && list(item.excludedKits).includes(hero.damageKit)) {
      return `Does not work with a ${hero.damageKit.toLowerCase()} kit`;
    }
    return null;
  }

  // Ladder step 4: Reserved For (allocation). Fires only when a named claimant
  // is in this roster and does not already hold the item. Claimants are
  // ordered, so the first eligible one gets the move prompt.
  function reservationClaimant(hero, item, roster, holds) {
    const claimants = list(item && item.reservedClaimants);
    if (!claimants.length || claimants.includes(hero.name)) return null;
    for (const claimant of claimants) {
      const member = list(roster).find((r) => r.name === claimant);
      if (member && !holds(member, item.name)) return claimant;
    }
    return null;
  }

  // Steps 1-4 are item-driven and shared by every slot that has a reference
  // record carrying exclusions and reservations.
  function itemSteps(opts) {
    const { hero, item, roster, context, holds } = opts;

    const unknown = cannotEvaluateExclusion(hero, item, context);
    if (unknown) return result(MARK.GREY, 2, unknown);

    const excluded = exclusionReason(hero, item, context);
    if (excluded) {
      if (isUnverified(item)) {
        return result(MARK.GREY, 3, "Possible mismatch, not yet verified in-game", { unverified: true });
      }
      return result(MARK.RED, 3, excluded, { replace: true });
    }

    const claimant = reservationClaimant(hero, item, roster, holds);
    if (claimant) return result(MARK.ORANGE, 4, `Move to ${claimant}`, { moveTo: claimant });

    return null;
  }

  // Worst mark of a set, used for the gear slot marker rollup. Locked sockets
  // (mark null) are ignored.
  function worstMark(results) {
    const marks = results.map((r) => r && r.mark).filter(Boolean);
    for (const mark of WORST_ORDER) if (marks.includes(mark)) return mark;
    return null;
  }

  // ── Ring ───────────────────────────────────────────────────────────────────

  // hero.ring = { T0, T1, T2 } confirmed path, ring names or empty.
  // equipped = ring name or empty. roster = [{ name, ring }] for the account.
  function evaluateRing({ hero, equipped, rings, roster, context }) {
    if (!equipped) return result(MARK.RED, 1, "Equip anything. Any ring beats no ring.");

    const item = rings[equipped];
    const holds = (member, ringName) => member.ring === ringName;
    const early = itemSteps({ hero, item: item || {}, roster, context, holds });
    if (early) return early;

    // Path-based marks (steps 6-8) do not depend on troop type, so a dual
    // hero's path evaluates normally whichever side they play.
    const path = hero.ring || {};
    const pathTiers = TIER_ORDER.filter((t) => path[t]);
    if (!pathTiers.length || !item) return result(MARK.GREY, 5, "No verified meta yet");

    // Target is the highest tier the hero has a confirmed target for.
    const targetTier = pathTiers[pathTiers.length - 1];
    const target = path[targetTier];

    if (equipped === target) {
      if (isUnverified(item)) return result(MARK.GREY, 6, "Meta match, not yet verified in-game", { unverified: true });
      return result(MARK.GREEN, 6, "");
    }

    const onPathTier = pathTiers.find((t) => path[t] === equipped);
    if (onPathTier && TIER_ORDER.indexOf(onPathTier) < TIER_ORDER.indexOf(targetTier)) {
      const next = pathTiers[pathTiers.indexOf(onPathTier) + 1];
      return result(MARK.ORANGE, 7, `Upgrade to ${path[next]}`, { upgradeTo: path[next] });
    }

    return result(MARK.ORANGE, 8, `Better option available: ${target}`, { target });
  }

  // ── Mount ──────────────────────────────────────────────────────────────────

  // hero.mount = { traits: [meta trait names] }. equipped = { traits, attributes }.
  // Temperament is never read: once equipped it has no effect (Mount KB v7 Rule 2).
  function evaluateMount({ hero, equipped, traits, roster, context }) {
    const equippedTraits = list(equipped && equipped.traits);
    if (!equippedTraits.length) return result(MARK.RED, 1, "Equip anything. Any mount beats no mount.");

    const holds = (member, traitName) => list(member.mountTraits).includes(traitName);
    for (const name of equippedTraits) {
      const early = itemSteps({ hero, item: traits[name] || {}, roster, context, holds });
      if (early) return early;
    }

    const metaTraits = list(hero.mount && hero.mount.traits);
    if (!metaTraits.length) return result(MARK.GREY, 5, "No verified meta yet");

    const missing = metaTraits.filter((t) => !equippedTraits.includes(t));
    const attributes = list(equipped.attributes);
    const attributeGaps = metaTraits.filter((t) => {
      const record = traits[t];
      return record && record.requiresAttributeMatch && record.attribute && !attributes.includes(record.attribute);
    });

    if (!missing.length && !attributeGaps.length) {
      if (metaTraits.some((t) => isUnverified(traits[t]))) {
        return result(MARK.GREY, 6, "Meta match, not yet verified in-game", { unverified: true });
      }
      return result(MARK.GREEN, 6, "");
    }
    if (!missing.length) {
      const gap = traits[attributeGaps[0]];
      return result(MARK.ORANGE, 8, `Better option available: ${gap.name} with ${gap.attribute}`, {
        target: metaTraits,
      });
    }
    return result(MARK.ORANGE, 8, `Better option available: ${metaTraits.join(" + ")}`, { target: metaTraits });
  }

  // ── Adornment ──────────────────────────────────────────────────────────────

  // Orientation precedence: Archer always Defense, then pure support Defense,
  // then damage dealer Attack. Damage Support is neither pure support nor a
  // pure damage dealer, so it returns null and the form marks grey.
  function adornmentOrientation(hero, troop) {
    if (troop === "ARC") return "Defense";
    if (hero.cardRole === "Tank Support" || hero.cardRole === "Healer Support") return "Defense";
    if (hero.cardRole === "DPS Lead") return "Attack";
    return null;
  }

  // equipped = form name or empty. Troop type comes from the current march.
  function evaluateAdornmentForm({ hero, equipped, context }) {
    if (!equipped) {
      if (isGatheringHero(hero)) return result(MARK.GREY, 1, "Adornments are combat-only, no spend needed here", { neutral: true });
      return result(MARK.RED, 1, "Equip anything. Any adornment beats an empty slot.");
    }
    const unknown = cannotEvaluateExclusion(hero, null, context);
    if (unknown) return result(MARK.GREY, 2, unknown);

    const troop = currentTroop(hero, context);
    const forms = ADORNMENT_FORMS[troop];
    const orientation = adornmentOrientation(hero, troop);
    if (!forms || !orientation) return result(MARK.GREY, 5, "No verified meta yet");

    const target = forms[orientation];
    if (equipped === target) return result(MARK.GREEN, 6, "");
    return result(MARK.ORANGE, 8, `Better option available: ${target}`, { target });
  }

  // hero.adornment = { effects: [meta effect names] }. equipped = effect name or empty.
  function evaluateAdornmentEffect({ hero, equipped, effects, roster, context }) {
    if (!equipped) {
      if (isGatheringHero(hero)) return result(MARK.GREY, 1, "Adornments are combat-only, no spend needed here", { neutral: true });
      return result(MARK.RED, 1, "Roll a special effect. Any effect beats none.");
    }

    const item = effects[equipped] || {};
    const holds = (member, effectName) => member.adornmentEffect === effectName;
    const early = itemSteps({ hero, item, roster, context, holds });
    if (early) return early;

    const meta = list(hero.adornment && hero.adornment.effects);
    if (!meta.length) return result(MARK.GREY, 5, "No verified meta yet");

    if (meta.includes(equipped)) {
      if (isUnverified(item)) return result(MARK.GREY, 6, "Meta match, not yet verified in-game", { unverified: true });
      return result(MARK.GREEN, 6, "");
    }
    return result(MARK.ORANGE, 8, `Better option available: ${meta[0]}`, { target: meta[0] });
  }

  // ── Gems ───────────────────────────────────────────────────────────────────

  // One socket. target = the hero's meta gem type for this socket's category.
  // gemTypes[name] = { name, isPlaceholder, placeholderFor: [names], dataStatus }.
  function evaluateGem({ hero, equipped, target, gearLevel, socketIndex, gemTypes }) {
    if (gearLevel < GEM_SOCKET_UNLOCK[socketIndex]) {
      return result(null, "locked", `Unlocks at gear level ${GEM_SOCKET_UNLOCK[socketIndex]}`);
    }
    if (!equipped) return result(MARK.RED, 1, "Socket a gem. Any gem beats an empty socket.");
    if (!target) return result(MARK.GREY, 5, "No verified meta yet");
    // A single per-slot Meta Gem field can't hold two targets for a dual hero
    // (Task 13), so a dual hero's gem target is never trusted yet.
    if (isDualHero(hero)) return result(MARK.GREY, 5, "No verified meta yet for this troop type");

    const record = gemTypes[equipped] || {};
    if (equipped === target) {
      if (isUnverified(gemTypes[target])) return result(MARK.GREY, 6, "Meta match, not yet verified in-game", { unverified: true });
      return result(MARK.GREEN, 6, "");
    }
    if (record.isPlaceholder && list(record.placeholderFor).includes(target)) {
      return result(MARK.ORANGE, 8, `Better option available: ${target}`, { target, placeholder: true });
    }
    // Wrong type gives zero relevant buff: a functional mismatch.
    if (isUnverified(record)) return result(MARK.GREY, 3, "Possible mismatch, not yet verified in-game", { unverified: true });
    return result(MARK.RED, 3, `No buff for this hero. Use ${target}`, { target, replace: true });
  }

  // ── Gear pieces ────────────────────────────────────────────────────────────

  // equipped = { troopType, rarity, dataStatus } or empty. Meta rarity is Legendary.
  function evaluateGearPiece({ hero, equipped, context }) {
    if (!equipped) return result(MARK.RED, 1, "Equip anything. Any gear beats an empty slot.");
    const troop = currentTroop(hero, context);
    if (!troop) return result(MARK.GREY, 2, isDualHero(hero) ? "Dual troop type: current march troop type not known" : "Hero troop type not recorded");

    const unverified = isUnverified(equipped);
    if (equipped.troopType !== troop) {
      if (unverified) return result(MARK.GREY, 3, "Possible mismatch, not yet verified in-game", { unverified: true });
      return result(MARK.RED, 3, `This is ${equipped.troopType} gear. Use the ${troop} set`, { replace: true });
    }
    if (equipped.rarity === "Legendary") {
      if (unverified) return result(MARK.GREY, 6, "Meta match, not yet verified in-game", { unverified: true });
      return result(MARK.GREEN, 6, "");
    }
    // A levelled Epic outperforms a lv1 Legendary, so a lower rarity of the
    // right set is an upgrade path, never a red.
    return result(MARK.ORANGE, 7, `Upgrade to the Legendary ${troop} piece`, { upgradeTo: "Legendary" });
  }

  // Gear slot marker = worst mark of the piece and its unlocked gem sockets.
  function gearSlotMarker(pieceResult, gemResults) {
    return worstMark([pieceResult].concat(list(gemResults)));
  }

  // ── Skills ─────────────────────────────────────────────────────────────────

  // Skills 1 and 2 are fixed per hero. A mismatch means our data or the
  // screenshot read is wrong, never the player: grey, low confidence, never red.
  function evaluateFixedSkill({ equipped, meta }) {
    if (!meta) return result(MARK.GREY, 5, "No verified meta yet");
    if (!equipped) return result(MARK.GREY, "skills-fixed", "Could not read this skill", { lowConfidence: true });
    if (equipped === meta) return result(MARK.GREEN, 6, "");
    return result(MARK.GREY, "skills-fixed", "Doesn't match our records. We may have this hero's skills wrong", {
      lowConfidence: true,
    });
  }

  // Skills 3 and 4. meta = recommended skill name(s); alternates = acceptable
  // non-meta choices. Off-list is red; an empty alternates list is the safe default.
  function evaluateFlexSkill({ equipped, meta, alternates }) {
    if (!equipped) return result(MARK.RED, 1, "Learn a skill. Any skill beats an empty slot.");
    const metaList = list(meta);
    if (!metaList.length) return result(MARK.GREY, 5, "No verified meta yet");
    if (metaList.includes(equipped)) return result(MARK.GREEN, 6, "");
    if (list(alternates).includes(equipped)) {
      return result(MARK.ORANGE, 8, `Better option available: ${metaList[0]}`, { target: metaList[0] });
    }
    return result(MARK.RED, 3, `Wrong skill for this hero. Use ${metaList[0]}`, { target: metaList[0], replace: true });
  }

  return {
    MARK,
    GEM_SOCKET_UNLOCK,
    evaluateRing,
    evaluateMount,
    evaluateAdornmentForm,
    evaluateAdornmentEffect,
    evaluateGem,
    evaluateGearPiece,
    gearSlotMarker,
    evaluateFixedSkill,
    evaluateFlexSkill,
    worstMark,
  };
});
