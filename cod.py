import os
import discord
import requests
import xml.etree.ElementTree as ET
from discord.ext import tasks

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

XML_URL = "http://85.190.163.102:10710/feed/dedicated-server-stats.xml?code=0c77cbd246bbdae1ad09d6ef78780e78"

GUILD_ID = 1352176561436102737
VOICE_CHANNEL_ID = 1466767151267446953

UPDATE_INTERVAL = 60  # secunde (safe)

MONTHS_RO = {
    1: "IAN", 2: "FEB", 3: "MAR", 4: "APR",
    5: "MAI", 6: "IUN", 7: "IUL", 8: "AUG",
    9: "SEP", 10: "OCT", 11: "NOI", 12: "DEC"
}

intents = discord.Intents.default()
client = discord.Client(intents=intents)


def get_fs25_time():
    r = requests.get(XML_URL, timeout=10)
    root = ET.fromstring(r.text)

    server = root.find("Server")
    day_time = int(server.attrib["dayTime"])        # ms
    time_scale = server.attrib.get("timeScale", "x?")

    # convertim ms -> HH:MM
    total_seconds = (day_time // 1000) % 86400
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    return f"{hours:02d}:{minutes:02d}", time_scale


@client.event
async def on_ready():
    print(f"Botul este online ca {client.user}")
    update_channel.start()


@tasks.loop(seconds=UPDATE_INTERVAL)
async def update_channel():
    guild = client.get_guild(GUILD_ID)
    if not guild:
        return

    channel = guild.get_channel(VOICE_CHANNEL_ID)
    if not channel:
        return

    hour, scale = get_fs25_time()

    # DATA REALĂ (doar pentru an + lună)
    from datetime import datetime
    now = datetime.now()
    year = now.year
    month = MONTHS_RO[now.month]

    new_name = f"⏳{year} | 📅 {month} | ⏰ {hour} | ⏱️{scale}"

    if channel.name != new_name:
        await channel.edit(name=new_name)


if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN lipsește din Environment Variables")

client.run(DISCORD_TOKEN)
