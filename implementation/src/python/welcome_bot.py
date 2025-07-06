import discord
import os

with open("../../../discord_bot_token") as f:
    TOKEN = f.read().strip()

intents = discord.Intents.default()
intents.members = True  # required to receive member join events

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("------")


@client.event
async def on_member_join(member):
    # Try to find a channel named 'introductions'
    channel = discord.utils.get(member.guild.text_channels, name="introductions")
    if channel:
        await channel.send(
            f"🌙 Welcome {member.mention}! Please introduce yourself!\n"
            "✨ What's your name?\n"
            "✨ What are your hobbies?\n"
            "✨ Anything else you'd like to share?"
        )
    else:
        print("No #introductions channel found.")


client.run(TOKEN)
