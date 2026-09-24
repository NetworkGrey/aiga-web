// Run with: node --test hero_card/test/diff_rules.test.js
const test = require("node:test");
const assert = require("node:assert/strict");

const rules = require("../diff_rules.js");
const { rings, mountTraits, adornmentEffects, heroes, roster } = require("./fixtures.js");

function assertMark(actual, mark, step) {
  assert.equal(actual.mark, mark, `mark (message: "${actual.message}")`);
  assert.equal(actual.step, step, `step (message: "${actual.message}")`);
}

const ring = (heroName, equipped, context) =>
  rules.evaluateRing({ hero: heroes[heroName], equipped, rings, roster, context });

// ── Spec v1.0 test-case table: the Task 11 acceptance bar ───────────────────

test("1. Lu Bu, Ring of Daisy: orange upgrade via step 7", () => {
  const r = ring("Lu Bu", "Ring of Daisy");
  assertMark(r, "orange", 7);
  assert.equal(r.upgradeTo, "Ring of Night Wolf");
});

test("2. Timur, Radiant Guardian: orange move to Lu Bu via step 4", () => {
  const r = ring("Timur", "Radiant Guardian", { marchTroop: "CAV" });
  assertMark(r, "orange", 4);
  assert.equal(r.moveTo, "Lu Bu");
});

test("3. Diao Chan, Ring of Daisy: red via step 3", () => {
  assertMark(ring("Diao Chan", "Ring of Daisy"), "red", 3);
});

test("4. Rani Durgavati, Ring of Rhino: red via step 3", () => {
  assertMark(ring("Rani Durgavati", "Ring of Rhino", { marchTroop: "CAV" }), "red", 3);
});

test("5. Zhao Yun, Ring of Shark: orange via step 8, not red", () => {
  assertMark(ring("Zhao Yun", "Ring of Shark"), "orange", 8);
});

test("6. Attila, Ring of Night Wolf: orange move to Lu Bu via step 4", () => {
  const r = ring("Attila the Hun", "Ring of Night Wolf", { marchTroop: "CAV" });
  assertMark(r, "orange", 4);
  assert.equal(r.moveTo, "Lu Bu");
});

test("7. Any hero, no ring: red via step 1", () => {
  assertMark(ring("Generic CAV Lead", ""), "red", 1);
});

test("8. Tribhuwana, unverified ring: grey via step 5", () => {
  assertMark(ring("Tribhuwana", "Ring of Clover", { marchTroop: "SW" }), "grey", 5);
});

test("9. Any hero, correct trait with wrong temperament: green via step 6", () => {
  const r = rules.evaluateMount({
    hero: heroes["Generic CAV Lead"],
    equipped: { traits: ["Overpower"], attributes: ["Might"], temperament: "Alert" },
    traits: mountTraits, roster,
  });
  assertMark(r, "green", 6);
});

test("10. Any hero, Overpower without Might: orange via step 8", () => {
  const r = rules.evaluateMount({
    hero: heroes["Generic CAV Lead"],
    equipped: { traits: ["Overpower"], attributes: ["Strategy"] },
    traits: mountTraits, roster,
  });
  assertMark(r, "orange", 8);
});

test("11. Timur, Lifesaver only: green via step 6", () => {
  const r = rules.evaluateMount({
    hero: heroes.Timur, equipped: { traits: ["Lifesaver"], attributes: [] },
    traits: mountTraits, roster, context: { marchTroop: "CAV" },
  });
  assertMark(r, "green", 6);
});

test("12. Diao Chan, no adornment: grey and neutral via the step 1 exception", () => {
  for (const evaluate of [rules.evaluateAdornmentForm, rules.evaluateAdornmentEffect]) {
    const r = evaluate({ hero: heroes["Diao Chan"], equipped: "", effects: adornmentEffects, roster });
    assertMark(r, "grey", 1);
    assert.equal(r.neutral, true);
  }
});

test("13. Hua Mulan, Lightning Strike: green via step 6", () => {
  const r = rules.evaluateAdornmentEffect({
    hero: heroes["Hua Mulan"], equipped: "Lightning Strike", effects: adornmentEffects, roster,
  });
  assertMark(r, "green", 6);
});

test("14. A CAV lead, Rally: red via step 3", () => {
  const r = rules.evaluateAdornmentEffect({
    hero: heroes["Generic CAV Lead"], equipped: "Rally", effects: adornmentEffects, roster,
  });
  assertMark(r, "red", 3);
});

test("15. Yodit, Lu Bu's skills on record: grey, low confidence, never red", () => {
  const yodit = heroes.Yodit;
  for (const [equipped, meta] of [["Wrath Forged Blade", yodit.skills.skill1], ["Shadow of Terror", yodit.skills.skill2]]) {
    const r = rules.evaluateFixedSkill({ equipped, meta });
    assertMark(r, "grey", "skills-fixed");
    assert.equal(r.lowConfidence, true);
  }
});

// ── Invariants and per-slot rules outside the table ──────────────────────────

test("a reserved item never moves when the wearer is the claimant", () => {
  assertMark(ring("Lu Bu", "Radiant Guardian"), "green", 6);
});

test("reservation lifts when the claimant is not in the roster", () => {
  const r = rules.evaluateRing({
    hero: heroes.Timur, equipped: "Radiant Guardian", rings,
    roster: [{ name: "Timur", ring: "Radiant Guardian" }], context: { marchTroop: "CAV" },
  });
  assertMark(r, "orange", 8);
});

test("a dual hero's ring path evaluates normally whichever side they play", () => {
  for (const marchTroop of ["CAV", "ARC"]) {
    assertMark(ring("Timur", "Tranquil Water", { marchTroop }), "green", 6);
  }
});

test("a dual hero's gem target stays grey until Task 13", () => {
  const r = rules.evaluateGem({ hero: heroes.Timur, equipped: "Might", target: "Might", gearLevel: 80, socketIndex: 0, gemTypes: {} });
  assertMark(r, "grey", 5);
});

test("unknown role greys the ring at step 2", () => {
  const hero = Object.assign({}, heroes["Lu Bu"], { cardRole: "" });
  assertMark(rules.evaluateRing({ hero, equipped: "Ring of Daisy", rings, roster }), "grey", 2);
});

test("dual hero with no march troop type greys at step 2", () => {
  assertMark(ring("Attila the Hun", "Ring of Night Wolf"), "grey", 2);
});

test("kit-based exclusion needs the hero's damage kit, else grey at step 2", () => {
  const hero = Object.assign({}, heroes.Timur, { damageKit: "" });
  const r = rules.evaluateRing({ hero, equipped: "Radiant Guardian", rings, roster, context: { marchTroop: "CAV" } });
  assertMark(r, "grey", 2);
});

test("an unverified record never drives a confident red", () => {
  const unverified = Object.assign({}, rings, {
    "Ring of Daisy": Object.assign({}, rings["Ring of Daisy"], { dataStatus: "Needs in-game check" }),
  });
  const r = rules.evaluateRing({ hero: heroes["Diao Chan"], equipped: "Ring of Daisy", rings: unverified, roster });
  assertMark(r, "grey", 3);
});

test("gems: right type green at any rarity, placeholder orange, wrong type red", () => {
  const gemTypes = {
    Might: { name: "Might" },
    "All Attributes": { name: "All Attributes", isPlaceholder: true, placeholderFor: ["Might"] },
    "Passive Skill Damage": { name: "Passive Skill Damage" },
  };
  const hero = heroes["Lu Bu"];
  const gem = (equipped) => rules.evaluateGem({ hero, equipped, target: "Might", gearLevel: 80, socketIndex: 0, gemTypes });
  assertMark(gem("Might"), "green", 6);
  assertMark(gem("All Attributes"), "orange", 8);
  assertMark(gem("Passive Skill Damage"), "red", 3);
});

test("gems: a locked socket carries no mark, an empty unlocked one is red", () => {
  const hero = heroes["Lu Bu"];
  assert.equal(rules.evaluateGem({ hero, equipped: "", target: "Might", gearLevel: 29, socketIndex: 1, gemTypes: {} }).mark, null);
  assertMark(rules.evaluateGem({ hero, equipped: "", target: "Might", gearLevel: 30, socketIndex: 1, gemTypes: {} }), "red", 1);
});

test("gear: lower rarity of the right set is orange, another troop's set is red", () => {
  const hero = heroes["Lu Bu"];
  const piece = (troopType, rarity) => rules.evaluateGearPiece({ hero, equipped: { troopType, rarity, dataStatus: "In-game verified" } });
  assertMark(piece("CAV", "Legendary"), "green", 6);
  assertMark(piece("CAV", "Epic"), "orange", 7);
  assertMark(piece("SW", "Legendary"), "red", 3);
});

test("gear: every live Gear Pieces row is Needs in-game check, so no confident mark", () => {
  const r = rules.evaluateGearPiece({ hero: heroes["Lu Bu"], equipped: { troopType: "CAV", rarity: "Legendary", dataStatus: "Needs in-game check" } });
  assertMark(r, "grey", 6);
});

test("gear slot marker shows the worst of the piece and its unlocked gems", () => {
  const green = { mark: "green" }, red = { mark: "red" }, locked = { mark: null };
  assert.equal(rules.gearSlotMarker(green, [green, red, locked]), "red");
  assert.equal(rules.gearSlotMarker(green, [green, locked]), "green");
});

test("skills 3/4: meta green, alternate orange, off-list red, no meta grey", () => {
  const skill = (equipped, alternates) => rules.evaluateFlexSkill({ equipped, meta: "Weak Spot Attack", alternates });
  assertMark(skill("Weak Spot Attack"), "green", 6);
  assertMark(skill("Infuriation", ["Infuriation"]), "orange", 8);
  assertMark(skill("Infuriation", []), "red", 3);
  assertMark(rules.evaluateFlexSkill({ equipped: "Infuriation", meta: [] }), "grey", 5);
});

test("adornment form: orientation from the form name, Archer always Defense", () => {
  const form = (hero, equipped, context) => rules.evaluateAdornmentForm({ hero: heroes[hero], equipped, context });
  assertMark(form("Hua Mulan", "Eagle's Blessing"), "green", 6);
  assertMark(form("Hua Mulan", "Piercing Arrow"), "orange", 8);
  assertMark(form("Generic CAV Lead", "Unyielding Iron"), "green", 6);
});

test("red is only ever reached through step 1 or step 3", () => {
  const outcomes = [];
  for (const heroName of Object.keys(heroes)) {
    for (const equipped of ["", ...Object.keys(rings)]) {
      outcomes.push(ring(heroName, equipped, { marchTroop: heroes[heroName].troops[0] }));
    }
  }
  for (const r of outcomes.filter((o) => o.mark === "red")) assert.ok([1, 3].includes(r.step), `red via step ${r.step}`);
});
