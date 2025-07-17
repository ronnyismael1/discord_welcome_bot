#######################
#
# This module handles sending onboarding
# messages to new users and sending created
# lore images to the introduction channel.
#
#######################

import os
import discord
import asyncio
from contextlib import nullcontext
from db.onboarding_db import STATUS_COMPLETED, STATUS_WAITING, OnboardingDB
from modules.lore_image import generate_lore_image

db = OnboardingDB()
user_tasks = {}

ROLE_STAFF              = "Staff"
ROLE_UNVERIFIED         = "Unverified"
CHANNEL_STAFF_LOGS      = "staff-logs"
CHANNEL_INTRODUCTION    = "introductions"
CATEGORY_ONBOARDING     = "Onboarding"

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
        if ret == -1:
            print("Error onboarding user.")

    @client.event
    async def on_message(message):
        # Ignore bot's own messages
        if message.author == client.user:
            return

        # TARGET CHANNEL: any
        # PERMISSIONS: Any role
        # DESC:
        #   Starts onboarding for calling user
        #
        if message.content.strip() == "!test":
            await message.channel.send("🔧 Test command detected! Running welcome logic...")
            ret = await begin_onboarding(message.author)
            if ret == -1: print("Error onboarding user.")

        # TARGET CHANNEL: #start-here-*
        # PERMISSIONS: Any role
        # DESC:
        #   If user is onboarding and wants to restart
        #   questionnaire, they can type `!start`.
        #
        if message.channel.name.startswith("start-here-"):
            record = db.get_user(message.author.id)
            if record is None or record["channel_id"] != str(message.channel.id):
                return
            if message.content.strip().lower() == "!start":
                await restart_onboarding(client, message.author, message.channel)
            return

        # TARGET CHANNEL: #bot-manager
        # PERMISSIONS: Staff/admin only (via Discord perms)
        # DESC:
        #   Administrative commands for onboarding DB.
        # COMMANDS:
        #   `!db missing` - Lists all users in discord but not in DB
        #   `!db list` - Lists all users in DB
        #   `!db sync` - Syncs all users in discord but not in DB
        #   `!db onboard @<user>` - Onboard a specific user
        #   `!db force_onboard_all` - Onboard all users in discord server
        #
        if message.channel.name == "bot-manager":
            guild = message.guild
            content = message.content.strip()

            # list all commands
            if content == "!ls":
                commands = (
                    "`!db missing` - Lists all users in discord but not in DB\n"
                    "`!db list` - Lists all users in DB\n"
                    "`!db sync` - Syncs all users in discord but not in DB\n"
                    "`!db onboard @<user>` - Onboard a specific user\n"
                    "`!db force_onboard_all` - Onboard all users in discord server"
                )
                await message.channel.send(f"Available commands:\n{commands}")
                return

            # list all users in discord but not in DB
            if content == "!db missing":
                # Get all non-bot members in the server
                guild_members = [
                    m for m in message.guild.members if not m.bot
                ]

                # Get all user IDs from DB
                db_users = db.get_all_users()
                db_user_ids = set(int(u['user_id']) for u in db_users)

                # Find members NOT in DB
                missing = []
                for m in guild_members:
                    if m.id not in db_user_ids:
                        missing.append(f"<@{m.id}> ({m.id})")  # mention user + ID

                if missing:
                    msg_text = "\n".join(missing)
                    await message.channel.send(f"🙋 Users NOT in DB:\n{msg_text}")
                else:
                    await message.channel.send("✅ All users in Discord are already in the DB.")
                return

            # list all waiting users in DB
            if content == "!db list":
                records = db.get_all_users()
                if records:
                    msg_text = "\n".join(
                        [f"{r['username']} ({r['user_id']}) - {r['status']}" for r in records]
                    )
                    await message.channel.send(f"📋 Users in DB:\n{msg_text}")
                else:
                    await message.channel.send("📋 DB is empty.")
                return

            # sync — onboard everyone not in DB
            if content == "!db sync":
                count = 0
                for member in guild.members:
                    if not member.bot and db.get_user(member.id) is None:
                        await begin_onboarding(member)
                        count += 1
                await message.channel.send(f"✅ Synced! Onboarded {count} missing users.")
                return

            # onboard specific user
            if content.startswith("!db onboard"):
                if message.mentions:
                    target = message.mentions[0]
                    await begin_onboarding(target) # TODO: Add timeout handling here
                    await message.channel.send(f"✅ Onboarding started for {target.display_name}")
                else:
                    await message.channel.send("❌ Please mention a user.")
                return

            # onboard all users (force)
            if content == "!db force_onboard_all":
                count = 0
                for member in guild.members:
                    if not member.bot:
                        await begin_onboarding(member)
                        count += 1
                await message.channel.send(f"✅ Onboarded all users ({count})")
                return

            # unknown command fallback
            await message.channel.send("❌ Unknown admin command. Try: `!db list`, `!db sync`, `!db onboard @user`, `!db onboard_all`")


###################################
#
#  PRIVATE FUNCTIONS
#
###################################

async def restart_onboarding(client, user, channel):
    # cancel existing task
    task = user_tasks.get(user.id)
    if task and not task.done():
        task.cancel()
        await channel.send("**Previous onboarding cancelled.**")

    # reset DB state
    db.update_status(user.id, STATUS_WAITING)
    db.save_answers(user.id, {})

    # start new task
    new_task = asyncio.create_task(start_questionnaire(client, user, channel))
    user_tasks[user.id] = new_task


async def begin_onboarding(member):
    # add user to unverified role
    unverified_role = discord.utils.get(member.guild.roles, name=ROLE_UNVERIFIED)
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

    # staff_channel = discord.utils.get(member.guild.text_channels, name=CHANNEL_STAFF_LOGS)
    # if staff_channel:
    #     await staff_channel.send(
    #         f"{member.display_name} has been onboarded and is waiting to start in {onboarding_channel.mention}."
    #     )
    # else:
    #     print("No #staff-logs channel found.")

    return 0


async def create_onboarding_channel(member):
    # Look for a category or fallback to guild
    category = discord.utils.get(member.guild.categories, name=CATEGORY_ONBOARDING)
    overwrites = {
        member.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }

    # Staff role can also see
    staff_role = discord.utils.get(member.guild.roles, name=ROLE_STAFF)
    if staff_role:
        overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

    # Bot role can also see
    bot_member = member.guild.me
    bot_role = bot_member.top_role
    overwrites[bot_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

    # Check if it already exists
    channel_name = f"start-here-{member.name.lower()}-{member.id}"
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
        return 0

    except discord.Forbidden:
        print(f"Error in questionnaire invite to {member}.")

        # Record error in staff-logs
        channel = discord.utils.get(member.guild.text_channels, name=CHANNEL_STAFF_LOGS)
        if channel:
            await channel.send(f"❌ ERROR: Could not DM {member.mention}!")
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

        # Question 10 (optional photo)
        await channel.send("📷 Upload a photo that describes you (or type `!skip` to skip):")

        while True:
            try:
                msg = await client.wait_for("message", check=check, timeout=600)

                if msg.content.strip().lower() == "!skip":
                    answers["photo_path"] = None
                    break

                if msg.attachments:
                    attachment = msg.attachments[0]
                    file_ext = os.path.splitext(attachment.filename)[1].lower()
                    if file_ext in [".png", ".jpg", ".jpeg", ".webp"]:
                        # Save the image locally
                        photo_dir = os.path.join(os.path.dirname(__file__), "../images/lore_users/subphoto_users")
                        os.makedirs(photo_dir, exist_ok=True)
                        photo_path = os.path.join(photo_dir, f"photo_{member.id}{file_ext}")
                        await attachment.save(photo_path)
                        answers["photo_path"] = photo_path
                        break
                    else:
                        await channel.send("❌ Please upload an image (.png, .jpg, .jpeg, .webp) or type `!skip`.")
                else:
                    await channel.send("❌ Please upload an image or type `!skip`.")

            except asyncio.TimeoutError:
                answers["photo_path"] = None
                await channel.send("⏳ Timeout. Skipping photo.")
                break

        # Save all answers
        db.save_answers(member.id, answers)
        db.update_status(member.id, STATUS_COMPLETED)

        await generate_and_send_custom_usr_lore(client, member, channel)
        await confirm_and_clean(member, channel)

    except asyncio.TimeoutError:
        await channel.send(
            "⏳ Timeout: You took too long to respond. "
            "Please type `!start` to restart the questionnaire when ready."
        )
        db.update_status(member.id, STATUS_WAITING)


async def confirm_and_clean(member, channel):
    # remove Unverified role
    unverified_role = discord.utils.get(member.guild.roles, name=ROLE_UNVERIFIED)
    if unverified_role:
        await member.remove_roles(unverified_role, reason="Completed onboarding")
        print(f"Removed Unverified role from {member.display_name}")
    else:
        print("Unverified role not found when trying to remove it.")

    # update DB: mark completed
    db.update_status(member.id, STATUS_COMPLETED)

    await channel.send(
        "✅ Thanks! Just sent. If you wish to redo your card just send "
        "`!start` in this channel at any time."
    )

    # log in staff-logs
    staff_channel = discord.utils.get(member.guild.text_channels, name=CHANNEL_STAFF_LOGS)
    if staff_channel:
        await staff_channel.send(
            f"✅ {member.display_name} has completed onboarding and their Unverified role was removed."
        )
    else:
        print("No #staff-logs channel found.")

async def generate_and_send_custom_usr_lore(client, member, channel):
    answers = db.get_answers(member.id)

    image_path = generate_lore_image(answers, username=member.name, user_id=member.id)

    def check(m):
        return m.author == member and m.channel == channel

    await channel.send(
        f"Thank you for completing the questionnaire!",
        file=discord.File(image_path)
    )
    await channel.send(
        "Do you wish to send this to the introduction channel? `!yes`\n"
        "*To remake your introduction card, do `!start` to begin again...*"
    )
    try:
        while True:
            msg = await client.wait_for("message", check=check, timeout=600)
            content = msg.content.strip().lower()
            if content == "!yes":
                intro_channel = discord.utils.get(member.guild.text_channels, name="introductions")
                if intro_channel:
                    await intro_channel.send(
                        f"🌟 Welcome in, {member.mention}! Check out their lore!",
                        file=discord.File(image_path)
                    )
                break
            else:
                await channel.send("Please reply with `!yes` to send or `!start` to restart.")
    except asyncio.TimeoutError:
        await channel.send("⏳ Timeout: No response. Please type `!start` when ready.")


