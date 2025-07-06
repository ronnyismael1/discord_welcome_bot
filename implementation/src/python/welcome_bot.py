import discord
import os

with open("../../../discord_bot_token") as f:
    TOKEN = f.read().strip()

intents = discord.Intents.default()
intents.members = True  # to get member join events
intents.messages = True  # to get on_message events
intents.message_content = True  # REQUIRED to read message content


client = discord.Client(intents=intents)


###################################
#
#  PRIVATE FUNCTIONS
#
###################################

# Reference this later: This is still a good function
# async def send_welcome_message(member):
#     # Try to find a channel named 'introductions'
#     channel = discord.utils.get(member.guild.text_channels, name="introductions")
#     if channel:
#         await channel.send(
#             f"🌙 Welcome {member.mention}! Please introduce yourself!\n"
#             "✨ What's your name?\n"
#             "✨ What are your hobbies?\n"
#             "✨ Anything else you'd like to share?"
#         )
#     else:
#         print("No #introductions channel found.")


async def send_welcome_message(member):
    try:
        await member.send("🌙 Welcome {member.mention}! Please introduce yourself!")
        await member.send("✨ What is your name?")

        def check(m):
            return m.author == member and isinstance(m.channel, discord.DMChannel)

        msg = await client.wait_for("message", check=check)
        name_user = msg.content

        await member.send(f"Your name is {name_user}")

    except discord.Forbidden:
        print(f"Could not DM {member}.")

        # Could not find user to DM, so we will notify staff-logs about it
        guild = member.guild
        channel = discord.utils.get(guild.text_channels, name="staff-logs")
        if channel:
            await channel.send(f"ERROR: Could not DM {member.mention}!")
        else:
            print("No #staff-logs channel found.")


###################################
#
#   CLIENT LISTENING EVENTS
#
###################################


@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("------")


@client.event
async def on_member_join(member):
    await send_welcome_message(member)


@client.event
async def on_message(message):
    # Ignore bot's own messages
    if message.author == client.user:
        return

    # If user types "!test", trigger the welcome
    if message.content.strip() == "!test":
        await message.channel.send("🔧 Test command detected! Running welcome logic...")
        await send_welcome_message(message.author)


client.run(TOKEN)
