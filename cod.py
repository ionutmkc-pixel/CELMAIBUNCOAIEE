import os
import discord
import requests
import xml.etree.ElementTree as ET
from discord.ext import tasks

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SV_XML = os.getenv("SV_XML")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN lipsește din Environment Variables")

intents = discord.Intents.default()
intents.guilds = True

bot = discord.Bot(intents=intents)

@tasks.loop(minutes=1)
async def update_channel():
    try:
        # Citește XML-ul de la server
        resp = requests.get(SV_XML)
        tree = ET.fromstring(resp.content)
        dayTime = int(tree.attrib.get("dayTime", 0))
        timeSpeed = 3  # x3 - aici poți citi și din XML dacă serverul dă
        hours = (dayTime // 3600) % 24
        minutes = (dayTime // 60) % 60
        # Nume canal
        new_name = f"⏳2026 | 📅 IUN | ⏰ {hours:02}:{minutes:02} | ⏱️x{timeSpeed}"
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.edit(name=new_name)
    except Exception as e:
        print("Eroare update canal:", e)

@bot.event
async def on_ready():
    print(f"Botul este online ca {bot.user}")
    update_channel.start()

bot.run(DISCORD_TOKEN)
