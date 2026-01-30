@tasks.loop(minutes=1)
async def rename_channel():
    guild = bot.get_guild(GUILD_ID)
    channel = guild.get_channel(VOICE_CHANNEL_ID)
    if not channel:
        return

    try:
        response = requests.get(XML_URL, timeout=10)
        root = ET.fromstring(response.content)

        day_time = int(root.attrib["dayTime"])

        # 🔥 FS25 time corect
        ms_in_day = 24 * 60 * 60 * 1000
        current_ms = day_time % ms_in_day

        hours = current_ms // (60 * 60 * 1000)
        minutes = (current_ms % (60 * 60 * 1000)) // (60 * 1000)

        # 🔥 Zi / luna FS25
        total_days = day_time // ms_in_day
        day = (total_days % 30) + 1
        month_index = (total_days // 30) % 12

        LUNI = ["IAN","FEB","MAR","APR","MAI","IUN","IUL","AUG","SEP","OCT","NOI","DEC"]
        luna = LUNI[month_index]

        # multiplicatorul serverului tău
        multiplicator = 3

        new_name = f"2026 | {luna} | {hours:02d}:{minutes:02d} | x{multiplicator}"

        if channel.name != new_name:
            await channel.edit(name=new_name)
            print("✔ Canal actualizat:", new_name)

    except Exception as e:
        print("EROARE:", e)
