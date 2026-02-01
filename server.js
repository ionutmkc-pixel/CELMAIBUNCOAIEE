import express from "express";

const app = express();
const PORT = process.env.PORT || 3000;

// ====== ENV CONFIG ======
const NITRADO_BASE = process.env.NITRADO_BASE || "http://85.190.163.102:10710/feed";
const NITRADO_CODE = process.env.NITRADO_CODE || "";
const MAX_SLOTS_FALLBACK = parseInt(process.env.MAX_SLOTS || "6", 10);

const DISCORD_INVITE = process.env.DISCORD_INVITE || "https://discord.gg/Cc5zK3hFf7";
const SERVER_NAME = process.env.SERVER_NAME || "MAX AGRO Romania";

// If you want to show server IP:PORT publicly, set these (optional)
const SERVER_ADDRESS = process.env.SERVER_ADDRESS || ""; // e.g. "85.190.163.102:10710"

// ====== STATIC FILES ======
app.use(express.static("public", { extensions: ["html"] }));

// ====== SIMPLE IN-MEM CACHE (avoid hammering Nitrado) ======
let cache = {
  ts: 0,
  data: null,
  ok: false,
  err: null
};
const CACHE_TTL_MS = 15000; // refresh from Nitrado at most every 15s

function requireEnv() {
  if (!NITRADO_CODE) {
    return "Missing NITRADO_CODE env var.";
  }
  return null;
}

function buildUrl(path) {
  // path already includes query params except code
  const join = path.includes("?") ? "&" : "?";
  return `${NITRADO_BASE}/${path}${join}code=${encodeURIComponent(NITRADO_CODE)}`;
}

async function fetchText(url, timeoutMs = 12000) {
  const controller = new AbortController();
  const t = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(url, { signal: controller.signal });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.text();
  } finally {
    clearTimeout(t);
  }
}

function getAttr(tag, attrName) {
  // Very small XML helper: find attr="..."
  // Example: <Server ... dayTime="50725127" ... />
  const re = new RegExp(`${attrName}\\s*=\\s*"([^"]*)"`, "i");
  const m = tag.match(re);
  return m ? m[1] : null;
}

function findFirstTag(xml, tagName) {
  const re = new RegExp(`<\\s*${tagName}\\b[^>]*>`, "i");
  const m = xml.match(re);
  if (m) return m[0];

  // also support self-closing: <Server ... />
  const re2 = new RegExp(`<\\s*${tagName}\\b[^>]*/\\s*>`, "i");
  const m2 = xml.match(re2);
  return m2 ? m2[0] : null;
}

function findTagText(xml, tagName) {
  const re = new RegExp(`<\\s*${tagName}\\b[^>]*>([\\s\\S]*?)<\\s*\\/\\s*${tagName}\\s*>`, "i");
  const m = xml.match(re);
  return m ? (m[1] || "").trim() : null;
}

function parseMoneyFromCareer(xml) {
  // <statistics><money>52619</money></statistics> OR any <money>...
  const statsBlock = findTagText(xml, "statistics");
  if (statsBlock) {
    const m = findTagText(statsBlock, "money");
    if (m && !isNaN(Number(m))) return Number(m);
  }
  // fallback: first <money> in whole doc
  const m2 = findTagText(xml, "money");
  if (m2 && !isNaN(Number(m2))) return Number(m2);
  return null;
}

function parseMapTitleFromCareer(xml) {
  const t = findTagText(xml, "mapTitle");
  if (t) return t;
  const id = findTagText(xml, "mapId");
  return id || null;
}

function parseTimeFromStats(xml) {
  const serverTag = findFirstTag(xml, "Server");
  if (!serverTag) return null;

  const dayTimeRaw = getAttr(serverTag, "dayTime") || getAttr(serverTag, "daytime");
  if (!dayTimeRaw || isNaN(Number(dayTimeRaw))) return null;

  const ms = Math.floor(Number(dayTimeRaw));
  const totalMinutes = Math.floor(ms / 1000 / 60);
  const hh = Math.floor(totalMinutes / 60) % 24;
  const mm = totalMinutes % 60;
  return `${String(hh).padStart(2, "0")}:${String(mm).padStart(2, "0")}`;
}

function parsePlayersFromStats(xml) {
  // In many Nitrado feeds you have <player isUsed="true" .../> slots
  const playerTags = xml.match(/<\s*player\b[^>]*\/\s*>/gi) || [];
  if (playerTags.length === 0) {
    return { online: 0, slots: MAX_SLOTS_FALLBACK };
  }
  const slots = playerTags.length;
  let online = 0;

  for (const tag of playerTags) {
    const isUsed = (getAttr(tag, "isUsed") || getAttr(tag, "isused") || "").toLowerCase();
    if (isUsed === "true") online++;
  }

  if (online > slots) online = slots;
  if (online < 0) online = 0;
  return { online, slots };
}

async function buildStatus() {
  const missing = requireEnv();
  if (missing) {
    return {
      ok: false,
      error: missing,
      serverName: SERVER_NAME,
      discordInvite: DISCORD_INVITE,
      serverAddress: SERVER_ADDRESS
    };
  }

  const statsUrl = buildUrl("dedicated-server-stats.xml");
  const careerUrl = buildUrl("dedicated-server-savegame.html?file=careerSavegame");

  // Map image URL (we will proxy it via /api/map.jpg so code is hidden)
  // Nitrado supports params quality/size
  const mapImgUrl = buildUrl("dedicated-server-stats-map.jpg?quality=70&size=768");

  const [statsXml, careerXml] = await Promise.all([
    fetchText(statsUrl),
    fetchText(careerUrl)
  ]);

  const mapTitle = parseMapTitleFromCareer(careerXml);
  const money = parseMoneyFromCareer(careerXml);
  const timeHHMM = parseTimeFromStats(statsXml);
  const { online, slots } = parsePlayersFromStats(statsXml);

  return {
    ok: true,
    serverName: SERVER_NAME,
    discordInvite: DISCORD_INVITE,
    serverAddress: SERVER_ADDRESS,
    mapTitle,
    money,
    time: timeHHMM,
    playersOnline: online,
    slots,
    mapImageProxy: "/api/map.jpg", // served by this app
    updatedAt: new Date().toISOString()
  };
}

// ====== API: STATUS ======
app.get("/api/status", async (req, res) => {
  const now = Date.now();
  if (cache.data && now - cache.ts < CACHE_TTL_MS) {
    res.json(cache.data);
    return;
  }

  try {
    const data = await buildStatus();
    cache = { ts: now, data, ok: true, err: null };
    res.json(data);
  } catch (e) {
    const data = {
      ok: false,
      error: String(e?.message || e),
      serverName: SERVER_NAME,
      discordInvite: DISCORD_INVITE,
      serverAddress: SERVER_ADDRESS
    };
    cache = { ts: now, data, ok: false, err: data.error };
    res.json(data);
  }
});

// ====== API: MAP IMAGE (proxy so code stays hidden) ======
app.get("/api/map.jpg", async (req, res) => {
  const missing = requireEnv();
  if (missing) {
    res.status(500).send(missing);
    return;
  }

  try {
    const url = buildUrl("dedicated-server-stats-map.jpg?quality=70&size=768");
    const r = await fetch(url);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    res.setHeader("Content-Type", "image/jpeg");
    r.body.pipeTo(WritableStreamFromNode(res));
  } catch (e) {
    res.status(500).send("Failed to fetch map image");
  }
});

// Helper: pipe Web ReadableStream to Node response
function WritableStreamFromNode(res) {
  return new WritableStream({
    write(chunk) {
      res.write(Buffer.from(chunk));
    },
    close() {
      res.end();
    },
    abort() {
      res.end();
    }
  });
}

app.listen(PORT, () => {
  console.log(`FS25 status page running on port ${PORT}`);
});