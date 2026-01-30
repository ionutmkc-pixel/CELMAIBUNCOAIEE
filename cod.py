import discord
from discord.ext import tasks
import os
import requests
from datetime import datetime

# -----------------------------
# Variabile din Environment
# -----------------------------
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
SV_XML = os.getenv("SV_XML")
TIME_MULTIPLIER = float(os.getenv("TIME_MULTIPLIER", "1"))

# Verificăm dacă există toate variabilele
if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN lipsește din Environment Variables")
if not CHANNEL_ID:
    raise RuntimeError("CHANNEL_ID lipsește din Environment Variables")
if not SV_XML:
    raise RuntimeError("SV_XML lipsește din Environment Variables")

# -----------------------------
# Bot setup
# -----------------------------
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents)

# -----------------------------
# Funcție pentru citirea timpului din XML
# -----------------------------
def get_server_time():
    try:
        r = requests.get(SV_XML)
        r.raise_for_status()
        data = r.text

        # Extragem timpul din XML (format simplificat)
        # Exemplu: <time>2026-06-03 03:35:00</time>
        import re
        match = re.search(r"<time>(.*?)</time>", data)
        if match:
            time_str = match.group(1)
            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            return dt
    except Exception as e:
        print("Eroare la preluarea timpului de pe server:", e)
    return datetime.utcnow()  # fallback dacă nu se poate citi

# -----------------------------
# Task pentru redenumire canal
# -----------------------------
@tasks.loop(seconds=60)  # update la fiecare 60 secunde
async def update_channel_name():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("Canalul nu a fost găsit")
        return

    server_time = get_server_time()
    if not server_time:
        return

    # Aplicăm TIME_MULTIPLIER
    hour = (server_time.hour * TIME_MULTIPLIER) % 24
    minute = server_time.minute

    # Formatare nume canal cu emoji
    new_name = f"⏳{server_time.year} | 📅 {server_time.strftime('%b').upper()} | ⏰ {int(hour):02d}:{minute:02d} | ⏱️x{int(TIME_MULTIPLIER)}"

    try:
        await channel.edit(name=new_name)
        print(f"Canal actualizat: {new_name}")
    except discord.HTTPException as e:
        print("Eroare la update canal:", e)

# -----------------------------
# Eveniment on_ready
# -----------------------------
@bot.event
async def on_ready():
    print(f"Botul este online ca {bot.user}")
    update_channel_name.start()

# -----------------------------
# Pornim botul
# -----------------------------
bot.run(DISCORD_TOKEN)
