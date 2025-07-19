#######################
#
# This module performs health checks on startup.
# It checks for required channels and permissions in each guild,
# and also own permissions for the bot user.
#
# THIS NEEDS TO RUN FIRST BEFORE BOT DOES ANYTHING ELSE!!!
#
#######################

import discord

from modules.constants import (
    CATEGORY_ONBOARDING,
    CHANNEL_BOT_MANAGER,
    CHANNEL_STAFF_LOGS,
    CHANNEL_INTRODUCTION,
    CHANNEL_ANNOUNCEMENTS,
    ROLE_STAFF,
    ROLE_UNVERIFIED,
)

'''
All possible permissions for the bot
[
    'create_instant_invite',
    'kick_members',
    'ban_members',
    'administrator',
    'manage_channels',
    'manage_guild',
    'add_reactions',
    'view_audit_log',
    'priority_speaker',
    'stream',
    'read_messages',
    'view_channel',
    'send_messages',
    'send_tts_messages',
    'manage_messages',
    'embed_links',
    'attach_files',
    'read_message_history',
    'mention_everyone',
    'external_emojis',
    'use_external_emojis',
    'view_guild_insights',
    'connect',
    'speak',
    'mute_members',
    'deafen_members',
    'move_members',
    'use_voice_activation',
    'change_nickname',
    'manage_nicknames',
    'manage_roles',
    'manage_permissions',
    'manage_webhooks',
    'manage_expressions',
    'manage_emojis',
    'manage_emojis_and_stickers',
    'use_application_commands',
    'request_to_speak',
    'manage_events',
    'manage_threads',
    'create_public_threads',
    'create_private_threads',
    'external_stickers',
    'use_external_stickers',
    'send_messages_in_threads',
    'use_embedded_activities',
    'moderate_members',
    'view_creator_monetization_analytics',
    'use_soundboard',
    'create_expressions',
    'create_events',
    'use_external_sounds',
    'send_voice_messages',
    'send_polls',
    'create_polls',
    'use_external_apps'
]
'''

REQUIRED_PERMISSIONS = [
    "send_messages",
    "read_messages",
    "manage_channels",
    "view_channel",
    "attach_files",
    "read_message_history",
    "manage_messages",
    "manage_roles",
]

REQUIRED_ROLES = [
    ROLE_STAFF,
    ROLE_UNVERIFIED
]

REQUIRED_CATEGORIES = [
    CATEGORY_ONBOARDING,
]
REQUIRED_CHANNELS = [
    CHANNEL_BOT_MANAGER,
    CHANNEL_STAFF_LOGS,
    CHANNEL_INTRODUCTION,
    CHANNEL_ANNOUNCEMENTS,
]

'''
Channel visibility rules:
    CHANNEL_BOT_MANAGER:    Private, staff + bot
    CHANNEL_STAFF_LOGS:     Private, staff + bot
    CHANNEL_INTRODUCTION:   Public, hidden from unverified users
    CHANNEL_ANNOUNCEMENTS:  Public
'''

missing_perms = []
missing_roles = []
missing_categories = []
missing_channels = []

#########################################
# Client call
#########################################

async def run(client) -> bool:
    print("[health_check] Bot logged in. Running health checks…")
    all_ok = True
    for guild in client.guilds:
        ok = await run_health_check(guild, client.user)
        if not ok:
            all_ok = False
    return all_ok

#########################################
# Main health check logic
#########################################

async def run_health_check(guild: discord.Guild, bot_user: discord.User) -> bool:
    global missing_perms, missing_categories, missing_channels, missing_roles
    missing_perms = []
    missing_categories = []
    missing_channels = []
    missing_roles = []

    print(f"Checking guild: {guild.name}")

    await check_permissions_bot(guild, bot_user)
    await check_exist_roles(guild)
    await check_exist_categories(guild)
    await check_exist_channels(guild)

    await generate_report(guild)

    if missing_perms or missing_roles or missing_categories or missing_channels:
        print("Issues detected, attempting to repair...")
        await repair_server(guild)

        # Re-check after repair
        missing_perms = []
        missing_categories = []
        missing_channels = []
        missing_roles = []

        await check_permissions_bot(guild, bot_user)
        await check_exist_roles(guild)
        await check_exist_categories(guild)
        await check_exist_channels(guild)

        await generate_report(guild)

    return not (missing_perms or missing_roles or missing_categories or missing_channels)

#########################################
# Check functions
#########################################

async def check_permissions_bot(guild, bot_user):
    # bot_member = guild.get_member(bot_user.id)
    perms = guild.me.guild_permissions

    for perm in REQUIRED_PERMISSIONS:
        if not getattr(perms, perm, False):
            missing_perms.append(perm)

async def check_exist_roles(guild):
    existing_roles = [r.name for r in guild.roles]
    for required in REQUIRED_ROLES:
        if required not in existing_roles:
            missing_roles.append(required)

async def check_exist_categories(guild):
    existing_categories = [cat.name for cat in guild.categories]
    for required in REQUIRED_CATEGORIES:
        if required not in existing_categories:
            missing_categories.append(required)

async def check_exist_channels(guild):
    existing_channels = [ch.name for ch in guild.channels]
    for required in REQUIRED_CHANNELS:
        if required not in existing_channels:
            missing_channels.append(required)

#########################################
# Report & Repair functions
#########################################

async def generate_report(guild):
    if not (missing_perms or missing_roles or missing_categories or missing_channels):
        print(f"All checks passed for guild: {guild.name}")
        return

    print(f"Health Check Report for: {guild.name}")
    if missing_perms:
        print(f"Missing Permissions: {', '.join(missing_perms)}")
    if missing_roles:
        print(f"Missing Roles: {', '.join(missing_roles)}")
    if missing_categories:
        print(f"Missing Categories: {', '.join(missing_categories)}")
    if missing_channels:
        print(f"Missing Channels: {', '.join(missing_channels)}")

async def repair_server(guild):
    roles = {r.name: r for r in guild.roles}
    bot_member = guild.me
    bot_role = bot_member.top_role

    # Ensure required roles exist
    for role_name in REQUIRED_ROLES:
        if role_name not in roles:
            print(f"Creating missing role: {role_name}")
            new_role = await guild.create_role(
                name=role_name,
                mentionable=True,
                reason="Repairing missing role required for onboarding bot"
            )
            roles[role_name] = new_role

    staff_role = roles[ROLE_STAFF]
    unverified_role = roles[ROLE_UNVERIFIED]

    # Create missing categories
    for cat_name in missing_categories:
        print(f"Creating category: {cat_name}")
        await guild.create_category(name=cat_name)

    # Update after creation
    categories = {c.name: c for c in guild.categories}
    # category = categories.get(CATEGORY_ONBOARDING)

    # Create or fix channels
    for ch_name in missing_channels:
        print(f"Creating text channel: {ch_name}")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=True),
            bot_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }

        # Special cases
        if ch_name == CHANNEL_BOT_MANAGER:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                staff_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                bot_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            }
        elif ch_name == CHANNEL_STAFF_LOGS:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                staff_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                bot_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            }
        elif ch_name == CHANNEL_INTRODUCTION:
            overwrites[unverified_role] = discord.PermissionOverwrite(read_messages=False)

        await guild.create_text_channel(
            name=ch_name,
            overwrites=overwrites,
            reason="Repairing missing channel with proper permissions"
        )

    print("Repair attempts completed.")


