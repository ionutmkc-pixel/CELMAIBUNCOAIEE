import discord
from discord.ext import tasks
from datetime import datetime, timedelta

# --- Configurație directă ---
DISCORD_TOKEN = "MTQ2NDkwNDExMDY4Njk5NDYxOA.GGJzsr.GCbsoMtCmeW7zrSr7ANIbapYS576EXxdM6amrY"
CHANNEL_ID = 1466767151267446953  # ID-ul canalului tău de voce
TIME_MULTIPLIER = 3  # x3

# --- Discord bot ---
intents = discord.Intents.default()
intents.guilds = True

bot = discord.Bot(intents=intents)

# --- Mapare lună în română ---
LUNAS = ["IAN","FEB","MAR","APR","MAI","IUN","IUL","AUG","SEP","OCT","NOI","DEC"]

def format_channel_name():
    # ora reală a serverului multiplicată cu TIME_MULTIPLIER
    now = datetime.utcnow() + timedelta(hours=(TIME_MULTIPLIER-1))
    luna = LUNAS[now.month - 1]
    return f"⏳{now.year} | 📅 {luna} | ⏰ {now.hour:02d}:{now.minute:02d} |⏱️x{TIME_MULTIPLIER}"

@tasks.loop(seconds=60)
async def update_channel():
    guild = bot.guilds[0]  # primul server unde e botul
    channel = guild.get_channel(CHANNEL_ID)
    if channel and isinstance(channel, discord.VoiceChannel):
        new_name = format_channel_name()
        try:
            await channel.edit(name=new_name)
            print(f"✅ Canal actualizat: {new_name}")
        except discord.HTTPException as e:
            print(f"❌ Eroare la editarea canalului: {e}")

@bot.event
async def on_ready():
    print(f"Botul este online ca {bot.user}")
    update_channel.start()

bot.run(DISCORD_TOKEN)
