import os
import discord
import requests
import xml.etree.ElementTree as ET
from discord.ext import tasks

# ================== CONFIG ==================

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

GUILD_ID = 1352176561436102737
VOICE_CHANNEL_ID = 1466767151267446953

XML_URL = "http://85.190.163.102:10710/feed/dedicated-server-stats.xml?code=0c77cbd246bbdae1ad09d6ef78780e78"

MULTIPLICATOR = 3  # x3 timp server FS25

LUNI = ["IAN","FEB","MAR","APR","MAI","IUN","IUL","AUG","SEP","OCT","NOI","DEC"]

# ============================================

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"🟢 Bot online ca {bot.user}")
    update_voice_channel.start()

@tasks.loop(minutes=1)
async def update_voice_channel():
    guild = bot.get_guild(GUILD_ID)
    channel = guild.get_channel(VOICE_CHANNEL_ID)
    if not channel:
        return

    try:
        response = requests.get(XML_URL, timeout=10)
        root = ET.fromstring(response.content)

        # 🔥 FS25 dayTime (milisecunde)
        day_time = int(root.attrib["dayTime"])

        ms_in_day = 24 * 60 * 60 * 1000
        current_ms = day_time % ms_in_day

        hours = current_ms // (60 * 60 * 1000)
        minutes = (current_ms % (60 * 60 * 1000)) // (60 * 1000)

        # 🔥 Zi / luna FS25
        total_days = day_time // ms_in_day
        month_index = (total_days // 30) % 12
        luna = LUNI[month_index]

        # 🔊 Nume canal FINAL cu emoji
        new_name = (
            f"⏳2026 | 📅 {luna} | "
            f"⏰ {hours:02d}:{minutes:02d} | "
            f"⏱️x{MULTIPLICATOR}"
        )

        if channel.name != new_name:
            await channel.edit(name=new_name)
            print("🔄 Canal actualizat:", new_name)

    except Exception as e:
        print("❌ Eroare:", e)

bot.run(DISCORD_TOKEN)
