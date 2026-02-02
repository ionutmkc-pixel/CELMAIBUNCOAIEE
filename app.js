function formatMoney(n) {
  if (n === null || n === undefined) return "—";
  const v = Math.round(Number(n));
  return v.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".") + " €";
}

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

async function loadStatus() {
  try {
    const res = await fetch("/api/status", { cache: "no-store" });
    const data = await res.json();

    setText("serverName", data.serverName || "FS25 Server");
    document.getElementById("discordBtn").href = data.discord || "#";

    if (!data.ok) {
      setText("status", "Offline");
      setText("updatedAt", "Server unreachable");
      setText("players", "—");
      setText("time", "—");
      setText("money", "—");
      setText("mapTitle", "—");
      return;
    }

    // STATUS
    setText("status", "Online");

    // UPDATE TIME (client side)
    setText(
      "updatedAt",
      "Last update: " + new Date().toLocaleString()
    );

    // PLAYERS (string deja corect ex: 1/6)
    setText("players", data.players || "0/0");

    // TIME
    setText("time", data.time || "--:--");

    // ECONOMY
    setText("money", formatMoney(data.money));

    // MAP
    setText("mapTitle", data.mapTitle || "Unknown");

    // MAP IMAGE
    const img = document.getElementById("mapImg");
    if (img && data.mapImage) {
      img.src = data.mapImage + "&t=" + Date.now();
    }

  } catch (e) {
    setText("status", "Error");
    setText("updatedAt", "Failed to load data");
  }
}

loadStatus();
setInterval(loadStatus, 30000); // refresh la 30s