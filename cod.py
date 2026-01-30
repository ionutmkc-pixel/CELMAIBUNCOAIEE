import os
import discord
import requests
from discord.ext import tasks
import re

# Environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 1352176561436102737           # ID server
CATEGORY_ID = 1466741769587785846       # ID categoria de schimbat
XML_URL = "http://85.190.163.102:10710/feed/dedicated-server-stats.xml?code=0c77cbd246bbdae1ad09d6ef78780e78"

# Map lunilor FS25 (poți adapta după harta ta)
LUNI = ["IAN", "FEB", "MAR", "APR", "MAI", "IUN", "IUL", "AUG", "SEP", "OCT", "NOI", "DEC"]

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"Botul este online ca {bot.user}")
    rename_category.start()  # pornim task-ul periodic

@tasks.loop(minutes=1)
async def rename_category():
    guild = bot.get_guild(GUILD_ID)
    category = guild.get_channel(CATEGORY_ID)
    if category:
        try:
            # Citește XML-ul FS25
            response = requests.get(XML_URL)
            xml_text = response.text

            # Extrage dayTime
            match_time = re.search(r'dayTime="(\d+)"', xml_text)
            day_time = int(match_time.group(1)) if match_time else 0

            # FS25 dayTime este un contor mare, îl convertim în zi / oră / minut
            # Ajustează conversia după cum ai setările hărții tale
            total_minutes = day_time // 10000  # aproximativ
            hours = (total_minutes // 60) % 24
            minutes = total_minutes % 60
            fs25_day = (total_minutes // (24*60)) + 1  # ziua în joc

            # Extrage numărul de jucători online
            players = re.findall(r'<Player isUsed="true"/>', xml_text)
            num_players = len(players)

            # Lună (poți fixa în funcție de ziua FS25 sau folosești lună reală)
            # Exemplu: fiecare 30 de zile FS25 = 1 lună
            fs25_month_index = ((fs25_day - 1) // 30) % 12
            luna = LUNI[fs25_month_index]

            # Anul rămâne același sau poți calcula în funcție de ziua FS25
            anul = 2026

            # Format final: 2026 | IAN | 12:34 | x3
            new_name = f"{anul} | {luna} | {hours:02d}:{minutes:02d} | x{num_players}"

            await category.edit(name=new_name)
            print(f"Categoria redenumită în {new_name}")

        except Exception as e:
            print(f"Eroare la redenumirea categoriei: {e}")

bot.run(DISCORD_TOKEN)
