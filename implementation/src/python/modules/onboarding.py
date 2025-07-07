import discord
import asyncio
from contextlib import nullcontext
from db.onboarding_db import OnboardingDB
from modules.lore_image import generate_lore_image

db = OnboardingDB()

###################################
#
#   CLIENT LISTENING EVENTS
#
###################################

def register(client):
    @client.event
    async def on_ready():
        print(f"Logged in as {client.user} (ID: {client.user.id})")
        print("------")

    @client.event
    async def on_member_join(member):
        ret = await begin_onboarding(member)
        if ret == -1: print("Error onboarding user.")

    @client.event
    async def on_message(message):
        # Ignore bot's own messages
        if message.author == client.user:
            return

        # If user types "!test", trigger the welcome
        if message.content.strip() == "!test":
            await message.channel.send("🔧 Test command detected! Running welcome logic...")
            ret = await begin_onboarding(message.author)
            if ret == -1: print("Error onboarding user.")

        # Only care about `start-here` channels
        if not message.channel.name.startswith("start-here-"):
            return
        # Load the onboarding state from DB
        record = db.get_user(message.author.id)
        if record is None:
            return  # not in DB → ignore
        if record["channel_id"] != str(message.channel.id):
            return  # wrong channel → ignore
        if message.content.strip().lower() == "!start":
            await start_questionnaire(client, message.author, message.channel)

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
        return -1

    # begin onboarding
    onboarding_channel = await create_onboarding_channel(member)
    ret                = await send_welcome_message(member, onboarding_channel)

    db.add_user(
        member.id,
        str(member),
        onboarding_channel.id,
        onboarding_channel.name
    )

    # finished onboarding, remove user from unverified role
    # if unverified_role:
    #     await member.remove_roles(unverified_role, reason="Completed onboarding")
    #     print(f"Removed Unverified role from {member.display_name}")
 
    # log that the user finished onbaording 
    staff_channel = discord.utils.get(member.guild.text_channels, name="staff-logs")
    if staff_channel:
        await staff_channel.send(
            f"{member.display_name} has been onboarded and is waiting to start in {onboarding_channel.mention}."
        )
    else:
        print("No #staff-logs channel found.")

    return 0


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

    # Check if it already exists
    channel_name = f"start-here-{member.name}".lower()
    existing_channel = discord.utils.get(member.guild.text_channels, name=channel_name)

    if existing_channel:
        return existing_channel

    # Create the channel inside the category
    onboarding_channel = await member.guild.create_text_channel(
        channel_name,
        overwrites=overwrites,
        category=category,
        reason="Onboarding new member"
    )

    return onboarding_channel


async def send_welcome_message(member, channel):
    try:
        await channel.send(
            f"🌙 Welcome {member.mention}! "
            f"To view **#Introduction** channel and to generate your own introduction "
            f"card, please answer the following questions.\n"
            f"\n[Please respond `!start` to begin questionnaire]"
        )

        # def check(m):
        #     return m.author == member and m.channel == channel
        #
        # msg = await client.wait_for("message", check=check)
        #
        # while True:
        #     msg = await client.wait_for("message", check=check)
        #     if msg.content.strip().lower() == "!start":
        #         return msg.content

        return 0

        # def check(m):
        #     return m.author == member and m.channel == channel

        # msg = await client.wait_for("message", check=check)
        # name_user = msg.content
        #
        # await channel.send(f"Your name is: **{name_user}**. Thank you!")
        # return name_user
        #
    except discord.Forbidden:
        print(f"Error in questionnaire invite to {member}.")

        # Record error in staff-logs
        channel = discord.utils.get(member.guild.text_channels, name="staff-logs")
        if channel:
            await channel.send(f"ERROR: Could not DM {member.mention}!")
        else:
            print("No #staff-logs channel found.")
        return -1


async def start_questionnaire(client, member, channel):
    await channel.send("📋 Starting questionnaire…")

    answers = {}

    def check(m):
        return m.author == member and m.channel == channel

    try:
        # Question 1
        await channel.send("✨ What is your name?")
        msg = await client.wait_for("message", check=check, timeout=600)
        answers["name"] = msg.content

        # Question 2
        await channel.send("✨ What are your pronouns?")
        msg = await client.wait_for("message", check=check, timeout=600)
        answers["pronouns"] = msg.content

        # Question 3
        await channel.send("✨ What is a quote you like?")
        msg = await client.wait_for("message", check=check, timeout=600)
        answers["quote"] = msg.content

        # Question 4
        await channel.send("✨ Fun fact about you?")
        msg = await client.wait_for("message", check=check, timeout=600)
        answers["fact"] = msg.content

        # Question 5
        await channel.send("✨ Zodiac Sign?")
        msg = await client.wait_for("message", check=check, timeout=600)
        answers["zsign"] = msg.content

        # Question 6
        await channel.send("✨ Top 3 video games?")
        msg = await client.wait_for("message", check=check, timeout=600)
        answers["fav_games"] = msg.content

        # Question 7
        await channel.send("✨ Favorite show?")
        msg = await client.wait_for("message", check=check, timeout=600)
        answers["fav_show"] = msg.content

        # Question 8
        await channel.send("✨ Favorite song?")
        msg = await client.wait_for("message", check=check, timeout=600)
        answers["fav_song"] = msg.content

        # Question 9
        await channel.send("✨ Hobbies?")
        msg = await client.wait_for("message", check=check, timeout=600)
        answers["hobbies"] = msg.content

        # Question 10
        # await channel.send("✨ Upload a photo that describes you!")
        # msg = await client.wait_for("message", check=check, timeout=600)
        # answers["photo"] = msg.content

        # Save all answers
        db.save_answers(member.id, answers)
        db.update_status(member.id, "completed")
        
        await generate_and_send_custom_usr_lore(member)
        await confirm_and_clean(member, channel)

    except asyncio.TimeoutError:
        await channel.send(
            "⏳ Timeout: You took too long to respond. "
            "Please type `!start` to restart the questionnaire when ready."
        )
        db.update_status(member.id, "waiting")


async def confirm_and_clean(member, channel):
    # remove Unverified role
    unverified_role = discord.utils.get(member.guild.roles, name="Unverified")
    if unverified_role:
        await member.remove_roles(unverified_role, reason="Completed onboarding")
        print(f"Removed Unverified role from {member.display_name}")
    else:
        print("Unverified role not found when trying to remove it.")

    # update DB: mark completed
    db.update_status(member.id, "completed")

    await channel.send("✅ Thanks! Your onboarding is complete.")

    # log in staff-logs
    staff_channel = discord.utils.get(member.guild.text_channels, name="staff-logs")
    if staff_channel:
        await staff_channel.send(
            f"✅ {member.display_name} has completed onboarding and their Unverified role was removed."
        )
    else:
        print("No #staff-logs channel found.")

async def generate_and_send_custom_usr_lore(member):
    answers = db.get_answers(member.id)

    image_path = generate_lore_image(answers, username=member.name, user_id=member.id)

    intro_channel = discord.utils.get(member.guild.text_channels, name="introductions")
    if intro_channel:
        await intro_channel.send(
            f"🌟 {member.mention} has completed onboarding!",
            file=discord.File(image_path)
        )

