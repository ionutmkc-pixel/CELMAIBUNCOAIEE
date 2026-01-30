import os
import discord
from discord.ext import tasks
from datetime import datetime, timedelta
from dotenv import load_dotenv

# --- Încarcă variabilele din .env ---
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN lipsește din Environment Variables")

CHANNEL_ID = os.getenv("CHANNEL_ID")
if not CHANNEL_ID:
    raise RuntimeError("CHANNEL_ID lipsește din Environment Variables")
CHANNEL_ID = int(CHANNEL_ID)

TIME_MULTIPLIER = os.getenv("TIME_MULTIPLIER")
if not TIME_MULTIPLIER:
    raise RuntimeError("TIME_MULTIPLIER lipsește din Environment Variables")
TIME_MULTIPLIER = int(TIME_MULTIPLIER)

# --- Discord bot ---
intents = discord.Intents.default()
intents.guilds = True
bot = discord.Bot(intents=intents)

# --- Mapare lună în română ---
LUNAS = ["IAN","FEB","MAR","APR","MAI","IUN","IUL","AUG","SEP","OCT","NOI","DEC"]

def format_channel_name():
    now = datetime.utcnow() + timedelta(hours=(TIME_MULTIPLIER-1))
    luna = LUNAS[now.month - 1]
    return f"⏳{now.year} | 📅 {luna} | ⏰ {now.hour:02d}:{now.minute:02d} |⏱️x{TIME_MULTIPLIER}"

@tasks.loop(seconds=60)
async def update_channel():
    guild = bot.guilds[0]
    channel = guild.get_channel(CHANNEL_ID)
    if channel and isinstance(channel, discord.VoiceChannel):
        try:
            await channel.edit(name=format_channel_name())
            print(f"✅ Canal actualizat: {format_channel_name()}")
        except discord.HTTPException as e:
            print(f"❌ Eroare la editarea canalului: {e}")

@bot.event
async def on_ready():
    print(f"Botul este online ca {bot.user}")
    update_channel.start()

bot.run(DISCORD_TOKEN)
