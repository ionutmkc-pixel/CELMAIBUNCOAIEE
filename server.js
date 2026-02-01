import express from "express";
import path from "path";
import { fileURLToPath } from "url";

const app = express();
const PORT = process.env.PORT || 3000;

// pentru __dirname în ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ===== ENV =====
const NITRADO_BASE = process.env.NITRADO_BASE;
const NITRADO_CODE = process.env.NITRADO_CODE;
const MAX_SLOTS = parseInt(process.env.MAX_SLOTS || "6", 10);
const DISCORD_INVITE = process.env.DISCORD_INVITE || "";
const SERVER_NAME = process.env.SERVER_NAME || "FS25 Server";

// ===== SERVE FILES DIN ROOT =====
app.use(express.static(__dirname));

// ===== STATUS API (simplu) =====
app.get("/api/status", async (req, res) => {
  if (!NITRADO_BASE || !NITRADO_CODE) {
    return res.json({ ok: false, error: "Missing NITRADO env vars" });
  }

  try {
    const statsUrl = `${NITRADO_BASE}/dedicated-server-stats.xml?code=${NITRADO_CODE}`;
    const careerUrl = `${NITRADO_BASE}/dedicated-server-savegame.html?code=${NITRADO_CODE}&file=careerSavegame`;

    const [statsRes, careerRes] = await Promise.all([
      fetch(statsUrl),
      fetch(careerUrl)
    ]);

    const stats = await statsRes.text();
    const career = await careerRes.text();

    // TIME
    const timeMatch = stats.match(/dayTime="(\d+)"/);
    let time = "--:--";
    if (timeMatch) {
      const mins = Math.floor(Number(timeMatch[1]) / 1000 / 60);
      time = `${String(Math.floor(mins / 60) % 24).padStart(2, "0")}:${String(mins % 60).padStart(2, "0")}`;
    }

    // PLAYERS
    const slots = (stats.match(/<player\b/gi) || []).length || MAX_SLOTS;
    const online = (stats.match(/isUsed="true"/gi) || []).length;

    // MONEY
    const moneyMatch = career.match(/<money>(\d+)<\/money>/);
    const money = moneyMatch ? Number(moneyMatch[1]) : null;

    // MAP
    const mapMatch = career.match(/<mapTitle>(.*?)<\/mapTitle>/);
    const mapTitle = mapMatch ? mapMatch[1] : "Unknown";

    res.json({
      ok: true,
      serverName: SERVER_NAME,
      discord: DISCORD_INVITE,
      time,
      players: `${online}/${slots}`,
      money,
      mapTitle,
      mapImage: `${NITRADO_BASE}/dedicated-server-stats-map.jpg?code=${NITRADO_CODE}`
    });
  } catch (e) {
    res.json({ ok: false, error: String(e) });
  }
});

// ===== START =====
app.listen(PORT, () => {
  console.log("FS25 site running on port", PORT);
});