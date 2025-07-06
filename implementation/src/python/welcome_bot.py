import discord
import os

# disable gateway logging while debugging
import logging
logging.getLogger("discord.gateway").setLevel(logging.ERROR)

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

async def begin_onboarding(member):
    # add user to unverified role
    unverified_role = discord.utils.get(member.guild.roles, name="Unverified")
    if unverified_role:
        await member.add_roles(unverified_role, reason="New member onboarding")
        print(f"Assigned Unverified role to {member.display_name}")
    else:
        print("Unverified role not found!")

    # begin onboarding
    onboarding_channel = await create_onboarding_channel(member)
    name_user          = await send_welcome_message(member, onboarding_channel)


    # finished onboarding, remove user from unverified role
    if unverified_role:
        await member.remove_roles(unverified_role, reason="Completed onboarding")
        print(f"Removed Unverified role from {member.display_name}")

    # log that the user finished onbaording 
    channel = discord.utils.get(member.guild.text_channels, name="staff-logs")
    if channel:
        await channel.send(f"{member.display_name} completed onboarding with name: {name_user}")
    else:
        print("No #staff-logs channel found.")


async def create_onboarding_channel(member):
    # Look for a category or fallback to guild
    category = discord.utils.get(member.guild.categories, name="Onboarding")
    overwrites = {
        member.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }

    # Staff role can also see
    staff_role = discord.utils.get(member.guild.roles, name="Staff")
    if staff_role:
        overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

    # Bot role can also see
    bot_member = member.guild.me
    bot_role = bot_member.top_role
    overwrites[bot_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

    # Create the channel inside the category
    channel_name = f"start-here-{member.name}".lower()
    onboarding_channel = await member.guild.create_text_channel(
        channel_name,
        overwrites=overwrites,
        category=category,
        reason="Onboarding new member"
    )

    return onboarding_channel


async def send_welcome_message(member, channel):
    try:
        await channel.send(f"🌙 Welcome {member.mention}! Please introduce yourself!")
        await channel.send("✨ What is your name?")

        def check(m):
            return m.author == member and m.channel == channel

        msg = await client.wait_for("message", check=check)
        name_user = msg.content

        await channel.send(f"Your name is: **{name_user}**. Thank you!")
        return name_user

    except discord.Forbidden:
        print(f"Could not send welcome message to {member}.")

        # Record error in staff-logs
        channel = discord.utils.get(member.guild.text_channels, name="staff-logs")
        if channel:
            await channel.send(f"ERROR: Could not DM {member.mention}!")
        else:
            print("No #staff-logs channel found.")
        return None

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
    await begin_onboarding(member)


@client.event
async def on_message(message):
    # Ignore bot's own messages
    if message.author == client.user:
        return

    # If user types "!test", trigger the welcome
    if message.content.strip() == "!test":
        await message.channel.send("🔧 Test command detected! Running welcome logic...")
        await begin_onboarding(message.author)


client.run(TOKEN)
