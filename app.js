function formatMoney(n) {
  if (n === null || n === undefined) return "—";
  const v = Math.round(Number(n));
  const s = v.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  return `${s} €`;
}

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

async function load() {
  try {
    const r = await fetch("/api/status", { cache: "no-store" });
    const data = await r.json();

    setText("serverName", data.serverName || "FS25 Server Status");
    const discordBtn = document.getElementById("discordBtn");
    if (discordBtn) discordBtn.href = data.discordInvite || "#";

    if (!data.ok) {
      setText("status", "Offline / Error");
      setText("updatedAt", data.error ? `Error: ${data.error}` : "Error");
      setText("players", "—");
      setText("time", "—");
      setText("money", "—");
      setText("mapTitle", "—");
      return;
    }

    setText("status", "Online");
    setText("updatedAt", `Last update: ${new Date(data.updatedAt).toLocaleString()}`);

    setText("players", `${data.playersOnline}/${data.slots}`);
    setText("time", data.time || "—");
    setText("money", formatMoney(data.money));
    setText("mapTitle", data.mapTitle || "—");

    const img = document.getElementById("mapImg");
    if (img && data.mapImageProxy) {
      img.src = data.mapImageProxy + `?t=${Date.now()}`;
    }

    const addrCard = document.getElementById("addrCard");
    const addr = document.getElementById("serverAddr");
    if (data.serverAddress) {
      addrCard.style.display = "block";
      addr.textContent = data.serverAddress;
    } else {
      addrCard.style.display = "none";
    }
  } catch (e) {
    setText("status", "Offline / Error");
    setText("updatedAt", "Failed to load status");
  }
}

load();
setInterval(load, 30000);