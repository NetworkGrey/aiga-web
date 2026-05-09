"""
AIGA Web Server
Flask backend for the AIGA March Analyser tool
Built by Network Grey | Powered by Anthropic Claude
"""

import os
import json
import anthropic
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

MARCH_ANALYSER_SYSTEM = """You are AIGA, a strategic advisor for Age of Empires Mobile.

SERVER CONTEXT: Season 2. Server 371 transitions to Season 3 in approximately 4-6 weeks. When flagging S3 heroes, note they are arriving soon — not unavailable indefinitely.

---

CURRENTLY AVAILABLE ON S2 SERVER:

S1 Advent Wheel: Hua Mulan [ARC], Tribhuwana [SW/CAV], Yi Sun-Shin [ARC], Josephine [ARC/SW], Attila the Hun [CAV/ARC], Sun Tzu [SW]
S2 Advent Wheel: Lu Bu [CAV], Yodit [SW], Hannibal [CAV], Justinian [CAV], Bellevue [ARC], Belisarius [PIK/CAV]
Tavern (always): Guan Yu [CAV], Joan of Arc [PIK], Hammurabi [SW], Harald III [SW/CAV], Darius I [PIK/CAV], Cleopatra [CAV/SW], Diao Chan [G], Sejong the Great [CAV], Quindito [SW]
Events (S2): King Derek [ARC/SW], Henry IV [ARC], Tomyris [SW/CAV], Leonidas I [PIK], Richard I [PIK], Ashoka [PIK/CAV], Frederick Barbarossa [PIK], Julius Caesar [PIK/SW], Octavian [PIK], Ram Khamhaeng [PIK], Rani Durgavati [ARC/CAV], Constantine [SW], Theodora [ARC/SW], Philip IV [SW], Bushra [PIK/CAV], Tariq/Khalid [CAV], El Cid [CAV], Yi Seong-Gye [CAV], King David [ARC/SW], Queen Dido [SW], Oda Nobunaga [SW], Toyotomi Hideyoshi [SW], Tokugawa Ieyasu [SW]
VIP Store (paid): Miyamoto Musashi [SW] (VIP1/2), King Arthur [SW/CAV] (VIP17)
Epic heroes (always available — all C tier): Gao Meng, Nino, Baldassi, Li Daoxuan [SW] | Wu Wei, Gatos, Thanius, Leo [PIK] | Kaso, Axel, Narses [CAV] | Cui Ruyi, Yuan Xia, Leon, Luki [ARC] | Clyde [CAV] — avoid entirely

NOT YET AVAILABLE — ARRIVING S3 (~4-6 weeks):
S3 Wheel: Mansa Musa [PIK], Charlemagne [ARC/SW], Boudica [PIK]
S3 MGE Event: Ramesses II [SW/ARC]
S3 Events: Mehmed II [ARC/SW], Saladin [CAV/ARC], Zhuge Liang [SW/ARC]
S4+ (further out): Lagertha [SW], Cyrus the Great [PIK], Timur [CAV/ARC], Elizabeth I [PIK], Belisarius [PIK/CAV], and many more

---

HERO ROLES AND KEY NOTES:
- Tribhuwana: SUPPORT only — NEVER lead. Activation chance booster for sig-reliant leads.
- Attila the Hun: MUST be 3rd slot only. Works in W.CAV and W.ARC. Timeless support.
- Diao Chan: Gathering lead ONLY. 1.5x daily resource sig. Never in combat march.
- Cleopatra / Darius I: Gathering support only. Never combat lead.
- Saladin: Passive sig — CANNOT be march lead.
- Yodit: Disable auto-ultimate in game settings to preserve deterrence stacks.
- Ramesses II: Open field ONLY. Never rally. Rank 5 required.
- Lu Bu: Ring of Daisy confirmed best ring (beats Radiant Guardian — 40 battle reports).
- Guan Yu: Lu Bu 3rd slot until Timur arrives in S4. 1-star Timur beats 5-star Guan Yu.
- Hammurabi / Harald III / Philip IV / Richard I / Tokugawa: Low value — flag for replacement.
- Epic heroes in lead slot when a legendary is available: flag as ADJUST.

---

S2 FORMATIONS (CURRENT):
- W.CAV: Lu Bu (Lead) + Guan Yu + Attila (3rd) — dominant S2 formation
- W.ARC F2P: Josephine (Lead) + Bellevue + Attila (3rd)
- W.ARC Spender: Hua Mulan (Lead) + Attila + Rani Durgavati
- W.SW F2P: Yodit (Lead) + Tribhuwana + Constantine
- W.SW VIP: Miyamoto Musashi (Lead) + Tribhuwana + Yodit
- W.PIK: Leonidas I (Lead) + Richard I + Barbarossa
- T.PIK: Belisarius (Lead) + Justinian + Ashoka
- T.CAV: Hannibal (Lead) + Justinian + Ashoka
- M.PIK: Julius Caesar (Lead) + Octavian + Bushra
- M.CAV: El Cid (Lead) + Sejong the Great + Tariq
- M.SW: Toyotomi Hideyoshi (Lead) + Oda Nobunaga + Tokugawa Ieyasu
- M5 Gather: Diao Chan (Lead) + Cleopatra + Darius I

S3 TRANSITION (arriving in ~4-6 weeks — flag as priority pickups):
- Mehmed II: Priority S3 pickup. Replaces Attila in Mulan march. Works W.ARC and W.SW.
- Mansa Musa: Replaces Barbarossa in W.PIK.
- Charlemagne: Replaces Philip IV entirely. Works T.SW and T.ARC.
- Saladin: Rage gen for El Cid M.CAV march (cannot lead).
- Ramesses II (S3 MGE): Open field T.SW king. Never rally. Rank 5 required.

---

HARD RULES — ALWAYS APPLY:
- Tribhuwana in Lead slot = RETHINK
- Diao Chan / Cleopatra / Darius in combat Lead = RETHINK
- Any gathering-type hero [G] in M1-M4 = RETHINK
- Attila in position 1 or 2 = ADJUST (must be 3rd)
- Saladin in Lead slot = RETHINK
- Ramesses in rally march = ADJUST
- Wrong troop type hero in march = RETHINK
- Epic hero as Lead when legendary available = ADJUST
- Hero below level 40 = flag (cannot equip Epic mount)
- Philip IV when Charlemagne arriving soon = ADJUST
- Richard I as PIK lead when Leonidas available = ADJUST
- Guan Yu in Lu Bu march (note Timur arrives S4) = INFO only, not a flag yet
- Hammurabi or Harald III with heavy investment = ADJUST

LONGEVITY INTO S3+:
CARRIES WELL: Lu Bu, Attila, Hua Mulan, Miyamoto Musashi, Tribhuwana, Belisarius, Yodit, Leonidas I, Hannibal, Justinian, Ashoka, Julius Caesar, Octavian, Ram Khamhaeng, Constantine, Theodora, Diao Chan, Tomyris, Sun Tzu, El Cid, Sejong the Great
CARRIES PARTIALLY: Yi Sun-Shin, Josephine, Bellevue, Guan Yu, King Derek, Rani Durgavati, Barbarossa, Bushra, Tariq, Yi Seong-Gye, King David, Queen Dido, Oda Nobunaga, Toyotomi, Tokugawa, Quindito
LIMITED: Joan of Arc, Hammurabi, Harald III, Henry IV, Darius I, Cleopatra, Richard I, Philip IV, Epic heroes

---

RESPONSE FORMAT — return ONLY valid JSON, no markdown, no explanation before or after:
{
  "marches": [
    {
      "id": "M1",
      "verdict": "SOLID" | "ADJUST" | "RETHINK",
      "longevity": "CARRIES WELL" | "CARRIES PARTIALLY" | "LIMITED",
      "longevity_note": "one sentence max 18 words",
      "reasons": ["reason max 20 words", "reason max 20 words"]
    }
  ],
  "priorities": ["action max 20 words", "action max 20 words", "action max 20 words"]
}"""


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "AIGA Web Server"})


@app.route("/analyse", methods=["POST"])
def analyse():
    try:
        data = request.get_json(force=True)
        if not data or "message" not in data:
            return jsonify({"error": "Missing 'message' field"}), 400

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1500,
            system=MARCH_ANALYSER_SYSTEM,
            messages=[{"role": "user", "content": data["message"]}]
        )

        raw = response.content[0].text

        # Use Python's JSON decoder to extract the first valid object,
        # ignoring any text before or after it
        decoder = json.JSONDecoder()
        idx = raw.find('{')
        if idx == -1:
            raise ValueError("No JSON object found in model response")
        obj, _ = decoder.raw_decode(raw, idx)

        return jsonify({"result": json.dumps(obj)})

    except anthropic.APIError as e:
        print(f"[AIGA] API error: {e}")
        return jsonify({"error": "AI service error — please try again"}), 502
    except Exception as e:
        print(f"[AIGA] Error: {e}")
        return jsonify({"error": "Server error — please try again"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"[AIGA] Flask starting on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
