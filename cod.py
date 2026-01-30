import discord
import requests
import xml.etree.ElementTree as ET
from discord.ext import tasks

# ===== CONFIGURAȚIE DIRECT ÎN COD =====
DISCORD_TOKEN = "MTQ2NDkwNDExMDY4Njk5NDYxOA.GL0noD.RtvscHmBmTiE1rv0Ms-U-yeLEXCQ6NtVrcSPOI"
CHANNEL_ID = 1466767151267446953
SV_XML = "http://85.190.163.102:10710/feed/dedicated-server-stats.xml?code=0c77cbd246bbdae1ad09d6ef78780e78"

# ===== SETUP BOT =====
intents = discord.Intents.default()
intents.guilds = True
bot = discord.Bot(intents=intents)

# ===== TASK PENTRU ACTUALIZAREA CANALULUI =====
@tasks.loop(minutes=1)
async def update_channel():
    try:
        # Citește XML server
        resp = requests.get(SV_XML)
        tree = ET.fromstring(resp.content)
        
        dayTime = int(tree.attrib.get("dayTime", 0))  # secunde de la start
        timeSpeed = 3  # multiplicatorul serverului (x3)
        
        # Calculează ora și minutul pe server
        hours = (dayTime // 3600) % 24
        minutes = (dayTime // 60) % 60
        
        # Format exact cu emoji
        new_name = f"⏳2026 | 📅 IUN | ⏰ {hours:02}:{minutes:02} | ⏱️x{timeSpeed}"
        
        # Ia canalul de voce
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.edit(name=new_name)
            print(f"Canal actualizat: {new_name}")
        else:
            print("Nu am găsit canalul de voce.")
    except Exception as e:
        print("Eroare la update canal:", e)

# ===== EVENIMENT LA PORNIRE BOT =====
@bot.event
async def on_ready():
    print(f"Botul este online ca {bot.user}")
    update_channel.start()  # pornește task-ul periodic

# ===== PORNIRE BOT =====
bot.run(DISCORD_TOKEN)
