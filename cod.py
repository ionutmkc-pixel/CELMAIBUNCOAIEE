import os
import discord
import requests
import xml.etree.ElementTree as ET
from discord.ext import tasks

# Environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 1352176561436102737
VOICE_CHANNEL_ID = 1466767151267446953
XML_URL = "http://85.190.163.102:10710/feed/dedicated-server-stats.xml?code=0c77cbd246bbdae1ad09d6ef78780e78"

LUNI = ["IAN", "FEB", "MAR", "APR", "MAI", "IUN", "IUL", "AUG", "SEP", "OCT", "NOI", "DEC"]

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"Botul este online ca {bot.user}")
    rename_channel.start()

@tasks.loop(minutes=5)  # actualizare la fiecare 5 minute
async def rename_channel():
    guild = bot.get_guild(GUILD_ID)
    channel = guild.get_channel(VOICE_CHANNEL_ID)
    if not channel:
        return

    try:
        # Citește XML FS25 pentru timp
        response = requests.get(XML_URL)
        root = ET.fromstring(response.content)

        # dayTime FS25
        day_time = int(root.attrib.get("dayTime", 0))
        total_minutes = day_time // 10000
        hours = (total_minutes // 60) % 24
        minutes = total_minutes % 60

        # Ziua FS25 și luna
        fs25_day = (total_minutes // (24*60)) + 1
        fs25_month_index = ((fs25_day - 1) // 30) % 12
        luna = LUNI[fs25_month_index]
        anul = 2026

        # Număr fix de jucători: x3
        num_players = 3

        # Format nume canal
        new_name = f"{anul} | {luna} | {hours:02d}:{minutes:02d} | x{num_players}"

        # Redenumește doar dacă s-a schimbat
        if channel.name != new_name:
            await channel.edit(name=new_name)
            print(f"Canalul de voce redenumit în {new_name}")

    except Exception as e:
        print(f"Eroare la redenumirea canalului: {e}")

bot.run(DISCORD_TOKEN)
