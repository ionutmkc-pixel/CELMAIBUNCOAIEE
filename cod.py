import os
import discord
from discord.ext import tasks
from datetime import datetime, timedelta

# ================== CONFIG ==================

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

GUILD_ID = 1352176561436102737
VOICE_CHANNEL_ID = 1466767151267446953

TIME_MULTIPLIER = 3          # x3 (schimbi în x5, x15 etc)
UPDATE_INTERVAL = 60         # secunde (NU mai mic!)

# ============================================

intents = discord.Intents.default()
client = discord.Client(intents=intents)

MONTHS_RO = {
    1: "IAN", 2: "FEB", 3: "MAR", 4: "APR",
    5: "MAI", 6: "IUN", 7: "IUL", 8: "AUG",
    9: "SEP", 10: "OCT", 11: "NOI", 12: "DEC"
}

@client.event
async def on_ready():
    print(f"Botul este online ca {client.user}")
    update_time.start()

@tasks.loop(seconds=UPDATE_INTERVAL)
async def update_time():
    guild = client.get_guild(GUILD_ID)
    if not guild:
        return

    channel = guild.get_channel(VOICE_CHANNEL_ID)
    if not channel:
        return

    # timp real
    now = datetime.now()

    # aplică x3
    multiplied_time = now + timedelta(
        seconds=now.timestamp() * (TIME_MULTIPLIER - 1)
    )

    year = multiplied_time.year
    month = MONTHS_RO[multiplied_time.month]
    hour = multiplied_time.strftime("%H:%M")

    new_name = f"⏳{year} | 📅 {month} | ⏰ {hour} | ⏱️x{TIME_MULTIPLIER}"

    if channel.name != new_name:
        await channel.edit(name=new_name)

# ================== START ==================

if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN nu este setat în Environment Variables")

client.run(DISCORD_TOKEN)
