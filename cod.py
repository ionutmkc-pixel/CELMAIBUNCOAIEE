import os
import json

settings_json = os.getenv("SETTINGS_JSON")
if not settings_json:
    raise RuntimeError("SETTINGS_JSON lipsește din Environment Variables")

settings = json.loads(settings_json)

DISCORD_TOKEN = settings["DISCORD_TOKEN"]
SV_XML = settings["SV_XML"]
CHANNEL_ID = settings["CHANNEL_ID"]

print("Token și setările SV au fost citite cu succes.")
