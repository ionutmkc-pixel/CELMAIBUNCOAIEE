import os
import discord
from discord.ext import tasks
from datetime import datetime, timedelta

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN lipsește din Environment Variables")

CHANNEL_ID = int(os.environ.get("CHANNEL_ID"))
TIME_MULTIPLIER = int(os.environ.get("TIME_MULTIPLIER"))

intents = discord.Intents.default()
intents.guilds = True
bot = discord.Bot(intents=intents)

LUNAS = ["IAN","FEB","MAR","APR","MAI","IUN","IUL","AUG","SEP","OCT","NOI","DEC"]

def format_channel_name():
    now = datetime.utcnow() + timedelta(hours=(TIME_MULTIPLIER-1))
    luna = LUNAS[now.month - 1]
    return f"⏳{now.year} | 📅 {luna} | ⏰ {now.hour:02d}:{now.minute:02d} |⏱️x{TIME_MULTIPLIER}"

@tasks.loop(seconds=60)
async def update_channel():
    if not bot.guilds:
        return
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