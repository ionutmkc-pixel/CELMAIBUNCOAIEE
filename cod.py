import os
import json
import discord
import requests
import xml.etree.ElementTree as ET
from discord.ext import tasks

# 1️⃣ Citește SETTINGS_JSON din Environment Variables
settings_json = os.getenv("SETTINGS_JSON")
if not settings_json:
    raise RuntimeError("SETTINGS_JSON lipsește din Environment Variables")

settings = json.loads(settings_json)

DISCORD_TOKEN = settings.get("DISCORD_TOKEN")
SV_XML = settings.get("SV_XML")
CHANNEL_ID = int(settings.get("CHANNEL_ID"))  # convertim la int

if not DISCORD_TOKEN or not SV_XML or not CHANNEL_ID:
    raise RuntimeError("Variabilele din SETTINGS_JSON nu sunt complete")

# 2️⃣ Setup bot
intents = discord.Intents.default()
intents.guilds = True  # pentru modificarea canalelor
bot = discord.Bot(intents=intents)

# 3️⃣ Functie pentru update canal
@tasks.loop(minutes=1)
async def update_channel():
    try:
        # Citește XML server
        resp = requests.get(SV_XML)
        tree = ET.fromstring(resp.content)
        
        dayTime = int(tree.attrib.get("dayTime", 0))  # secunde de la start
        timeSpeed = 3  # default x3 (poți lua și din XML dacă e specificat)
        
        # Calculează ora și minutul în server
        hours = (dayTime // 3600) % 24
        minutes = (dayTime // 60) % 60
        
        # Formatează numele canalului exact cum vrei
        new_name = f"⏳2026 | 📅 IUN | ⏰ {hours:02}:{minutes:02} | ⏱️x{timeSpeed}"
        
        # Ia canalul de voce
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.edit(name=new_name)
            print(f"Canal actualizat: {new_name}")
    except Exception as e:
        print("Eroare update canal:", e)

# 4️⃣ La pornire
@bot.event
async def on_ready():
    print(f"Botul este online ca {bot.user}")
    update_channel.start()  # pornește task-ul periodic

# 5️⃣ Pornire bot
bot.run(DISCORD_TOKEN)
