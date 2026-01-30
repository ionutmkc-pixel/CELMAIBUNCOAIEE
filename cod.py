import os
import json
import discord
from discord.ext import tasks
import requests
from datetime import datetime

# -----------------------------
# Citim SETTINGS_JSON
# -----------------------------
SETTINGS_JSON = os.getenv("SETTINGS_JSON")
if not SETTINGS_JSON:
    raise RuntimeError("SETTINGS_JSON lipsește din Environment Variables")

settings = json.loads(SETTINGS_JSON)

DISCORD_TOKEN = settings["DISCORD_TOKEN"]
CHANNEL_ID = int(settings["CHANNEL_ID"])
SV_XML = settings["SV_XML"]
TIME_MULTIPLIER = int(settings["TIME_MULTIPLIER"])

# -----------------------------
# Setup bot
# -----------------------------
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents)

# -----------------------------
# Funcție pentru citirea timpului de pe server
# -----------------------------
def get_server_time():
    try:
        r = requests.get(SV_XML, timeout=5)
        r.raise_for_status()
        data = r.text
        import re
        match = re.search(r"<time>(.*?)</time>", data)
        if match:
            time_str = match.group(1)
            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            return dt
    except Exception as e:
        print("Eroare la preluarea timpului de pe server:", e)
    return datetime.utcnow()  # fallback

# -----------------------------
# Task pentru actualizarea numelui canalului
# -----------------------------
@tasks.loop(seconds=60)
async def update_channel_name():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("Canalul nu a fost găsit")
        return

    server_time = get_server_time()
    hour = (server_time.hour * TIME_MULTIPLIER) % 24
    minute = server_time.minute

    new_name = f"⏳{server_time.year} | 📅 {server_time.strftime('%b').upper()} | ⏰ {hour:02d}:{minute:02d} | ⏱️x{TIME_MULTIPLIER}"

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
# Pornire bot
# -----------------------------
bot.run(DISCORD_TOKEN)
