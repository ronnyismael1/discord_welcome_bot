import os
import discord
import logging
from modules import onboarding

# disable gateway logging while debugging
logging.getLogger("discord.gateway").setLevel(logging.ERROR)

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)

# register all feature modules here
onboarding.register(client)

if __name__ == "__main__":
    with open("../../../discord_bot_token") as f:
        TOKEN = f.read().strip()
    client.run(TOKEN)

