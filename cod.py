import os
import discord
import requests
from discord.ext import tasks
import re

# Environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 1352176561436102737           # ID server
VOICE_CHANNEL_ID = 1466741769587785846  # ID canal de voce
XML_URL = "http://85.190.163.102:10710/feed/dedicated-server-stats.xml?code=0c77cbd246bbdae1ad09d6ef78780e78"

# Map lunilor FS25
LUNI = ["IAN", "FEB", "MAR", "APR", "MAI", "IUN", "IUL", "AUG", "SEP", "OCT", "NOI", "DEC"]

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"Botul este online ca {bot.user}")
    rename_channel.start()  # pornim task-ul periodic

@tasks.loop(minutes=1)
async def rename_channel():
    guild = bot.get_guild(GUILD_ID)
    channel = guild.get_channel(VOICE_CHANNEL_ID)
    if channel:
        try:
            # Citește XML-ul FS25
            response = requests.get(XML_URL)
            xml_text = response.text

            # Extrage dayTime
            match_time = re.search(r'dayTime="(\d+)"', xml_text)
            day_time = int(match_time.group(1)) if match_time else 0

            # Convertește în ore și minute
            total_minutes = day_time // 10000
            hours = (total_minutes // 60) % 24
            minutes = total_minutes % 60

            # Numărul de jucători online
            players = re.findall(r'<Player isUsed="true"/>', xml_text)
            num_players = len(players)

            # Ziua FS25 și luna
            fs25_day = (total_minutes // (24*60)) + 1
            fs25_month_index = ((fs25_day - 1) // 30) % 12
            luna = LUNI[fs25_month_index]

            anul = 2026

            # Format nume canal de voce
            new_name = f"{anul} | {luna} | {hours:02d}:{minutes:02d} | x{num_players}"

            await channel.edit(name=new_name)
            print(f"Canalul de voce redenumit în {new_name}")

        except Exception as e:
            print(f"Eroare la redenumirea canalului: {e}")

bot.run(DISCORD_TOKEN)
