import discord
from discord.ext import tasks
import os
import requests
from datetime import datetime

# -----------------------------
# Variabile din Environment (completate cu datele tale)
# -----------------------------
DISCORD_TOKEN = "MTQ2NDkwNDExMDY4Njk5NDYxOA.GL0noD.RtvscHmBmTiE1rv0Ms-U-yeLEXCQ6NtVrcSPOI"
CHANNEL_ID = 1466767151267446953  # ID canal voce
SV_XML = "http://85.190.163.102:10710/feed/dedicated-server-stats.xml?code=0c77cbd246bbdae1ad09d6ef78780e78"
TIME_MULTIPLIER = 3  # x3 server time

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
        r = requests.get(SV_XML)
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
    # fallback la UTC dacă nu merge XML
    return datetime.utcnow()

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

    # Formatul exact cerut cu emoji
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
# Pornire bot
# -----------------------------
bot.run(DISCORD_TOKEN)
