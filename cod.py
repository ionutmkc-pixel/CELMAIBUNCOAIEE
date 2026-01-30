import discord
from discord.ext import tasks, commands
import requests
import xml.etree.ElementTree as ET
import os

# ---------------- CONFIGURAȚIE ----------------
XML_URL = "http://85.190.163.102:10710/feed/dedicated-server-stats.xml?code=0c77cbd246bbdae1ad09d6ef78780e78"
CHANNEL_ID = 1466741769587785846
DISCORD_TOKEN = os.getenv("MTQ2NDkwNDExMDY4Njk5NDYxOA.GDeUds.Nk5PRARaEHDmoOHKVDAZEdYdo37oclcYd6TkaY")
UPDATE_INTERVAL = 60
# ---------------------------------------------

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def convert_daytime(daytime):
    try:
        dt = int(daytime)
        total_minutes = dt // 1000 // 60
        hours = (total_minutes // 60) % 24
        minutes = total_minutes % 60
        days = (total_minutes // 60) // 24 + 1
        return f"Zi {days}, Ora {hours:02d}:{minutes:02d}"
    except:
        return "Timp invalid"

@bot.event
async def on_ready():
    print(f"Botul este online ca {bot.user}")
    update_time.start()

@tasks.loop(seconds=UPDATE_INTERVAL)
async def update_time():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("Canalul Discord nu a fost găsit!")
        return
    try:
        response = requests.get(XML_URL, timeout=10)
        root = ET.fromstring(response.content)
        dayTime = root.attrib.get("dayTime")
        human_time = convert_daytime(dayTime) if dayTime else "Nu s-a găsit dayTime"
        await channel.send(f"🕒 Ora serverului FS25: {human_time}")
    except Exception as e:
        print("Eroare XML:", e)
        await channel.send("⚠️ Nu am putut citi XML-ul serverului!")

bot.run(DISCORD_TOKEN)
