/*
 * Hardcoded fixture for the Diff Rules Spec v1.0 test-case table.
 *
 * Built from the spec, not from live Airtable: most of these values are not
 * populated yet (Task 12). Each record carries only the fields a test needs.
 * Structured exclusions mirror the Excluded For (functional) prose on the
 * live record, in the vocabulary of the Excluded Roles / Troops / Kits fields.
 * Re-verify against real Airtable data at Task 11.
 */

const VERIFIED = "In-game verified";
const COMBAT_ROLES = ["DPS Lead", "Damage Support", "Tank Support", "Healer Support"];
const NOT_SECOND_STRIKE = ["Passive", "Active", "Turn-based", "Stack"];

const rings = {
  "Ring of Daisy": {
    name: "Ring of Daisy", tier: "T0", dataStatus: VERIFIED,
    excludedRoles: ["Healer Support", "Gathering"],
  },
  "Ring of Night Wolf": {
    name: "Ring of Night Wolf", tier: "T1", dataStatus: VERIFIED,
    excludedRoles: ["Healer Support", "Gathering", "Siege"],
    reservedClaimants: ["Lu Bu"],
  },
  "Radiant Guardian": {
    name: "Radiant Guardian", tier: "T2", dataStatus: VERIFIED,
    excludedKits: NOT_SECOND_STRIKE,
    reservedClaimants: ["Lu Bu"],
  },
  "Ring of Rhino": {
    name: "Ring of Rhino", tier: "T1", dataStatus: VERIFIED,
    excludedRoles: COMBAT_ROLES.concat(["Gathering"]),
  },
  "Ring of Shark": {
    name: "Ring of Shark", tier: "T1", dataStatus: VERIFIED,
    excludedRoles: ["DPS Lead", "Healer Support", "Gathering"],
  },
  "Lord of Eastern Heavens": {
    name: "Lord of Eastern Heavens", tier: "T2", dataStatus: VERIFIED,
    excludedRoles: ["Gathering", "Siege"], excludedKits: ["Active"],
  },
  "Ring of Clover": { name: "Ring of Clover", tier: "T0", dataStatus: VERIFIED, excludedRoles: ["Gathering"] },
  "Tranquil Water": {
    name: "Tranquil Water", tier: "T2", dataStatus: VERIFIED,
    excludedRoles: ["Gathering", "Siege"],
  },
};

const mountTraits = {
  Overpower: { name: "Overpower", requiresAttributeMatch: true, attribute: "Might", dataStatus: VERIFIED },
  Lifesaver: { name: "Lifesaver", requiresAttributeMatch: false, dataStatus: VERIFIED },
};

const adornmentEffects = {
  "Lightning Strike": {
    name: "Lightning Strike", dataStatus: VERIFIED,
    excludedKits: NOT_SECOND_STRIKE,
  },
  Rally: {
    name: "Rally", dataStatus: VERIFIED,
    excludedRoles: ["DPS Lead"],
  },
};

const heroes = {
  "Lu Bu": {
    name: "Lu Bu", troops: ["CAV"], cardRole: "DPS Lead", damageKit: "Second strike",
    ring: { T0: "Ring of Daisy", T1: "Ring of Night Wolf", T2: "Radiant Guardian" },
    skills: { skill1: "One of a Kind General", skill2: "Unrivaled Prowess" },
  },
  Timur: {
    name: "Timur", troops: ["CAV", "ARC"], cardRole: "Damage Support", damageKit: "Second strike",
    ring: { T2: "Tranquil Water" },
    mount: { traits: ["Lifesaver"] },
  },
  "Diao Chan": {
    name: "Diao Chan", troops: ["GATH"], cardRole: "Gathering",
  },
  "Rani Durgavati": {
    name: "Rani Durgavati", troops: ["ARC", "CAV"], cardRole: "Damage Support",
    ring: { T2: "Ring of Crow" },
  },
  "Zhao Yun": {
    name: "Zhao Yun", troops: ["CAV"], cardRole: "Damage Support", damageKit: "Passive",
    ring: { T2: "Lord of Eastern Heavens" },
  },
  "Attila the Hun": {
    name: "Attila the Hun", troops: ["CAV", "ARC"], cardRole: "Damage Support",
    ring: { T2: "Lofty Mountain" },
  },
  Tribhuwana: {
    name: "Tribhuwana", troops: ["SW", "CAV"], cardRole: "Damage Support",
    ring: {},
  },
  "Hua Mulan": {
    name: "Hua Mulan", troops: ["ARC"], cardRole: "DPS Lead", damageKit: "Second strike",
    adornment: { effects: ["Lightning Strike"] },
  },
  // Stand-ins for the spec's "Any hero" and "A CAV lead" rows.
  "Generic CAV Lead": {
    name: "Generic CAV Lead", troops: ["CAV"], cardRole: "DPS Lead", damageKit: "Passive",
    ring: { T0: "Ring of Clover" },
    mount: { traits: ["Overpower"] },
  },
  // Yodit's record currently carries Lu Bu's Skills 1 and 2 verbatim.
  Yodit: {
    name: "Yodit", troops: ["SW"], cardRole: "DPS Lead",
    skills: { skill1: "One of a Kind General", skill2: "Unrivaled Prowess" },
  },
};

// Lu Bu wears a T0 while a higher-priority ring sits elsewhere: the roster the
// Timur and Attila move prompts are evaluated against.
const roster = [
  { name: "Lu Bu", ring: "Ring of Daisy" },
  { name: "Timur", ring: "Radiant Guardian" },
  { name: "Attila the Hun", ring: "Ring of Night Wolf" },
];

module.exports = { rings, mountTraits, adornmentEffects, heroes, roster };
