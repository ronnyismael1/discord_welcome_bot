#######################
#
# This module is responsible for notifying
# users when gloomxmoon starts streaming.
#
# Need to check both twitch and tiktok
#
#######################

import os
import discord
import asyncio
import aiohttp

TARGET_USERNAME = "gloomxmoon"
ALERT_CHANNEL_NAME = "☾-𝒜𝔫𝔫𝔬𝔲𝔫𝔠𝔢𝔪𝔢𝔫𝔱𝔰・₊˚"

with open("../../../twitch_client_secret") as f:
    lines = [line.strip() for line in f.readlines()]
    TWITCH_CLIENT_ID = lines[0]
    TWITCH_CLIENT_SECRET = lines[1]

###################################
#
#   CLIENT LISTENING EVENTS
#
###################################

def register(client):
    """
    Registers the stream monitoring task with the client.
    """
    client.loop.create_task(monitor_stream(client))

async def monitor_stream(client):
    await client.wait_until_ready()
    was_live = False

    token = await get_twitch_token()
    print("[Twitch] Got access token")

    async with aiohttp.ClientSession() as session:
        while not client.is_closed():
            try:
                twitch_live = await check_twitch_live(session, token)
                tiktok_live = await check_tiktok_live(session)

                is_live = twitch_live or tiktok_live

                if is_live and not was_live:
                    print(f"[Stream] {TARGET_USERNAME} is live (Twitch: {twitch_live}, TikTok: {tiktok_live})")

                    for guild in client.guilds:
                        channel = discord.utils.get(
                            guild.text_channels,
                            name=ALERT_CHANNEL_NAME.lower()
                        )
                        if channel:
                            await channel.send(
                                f"✨ Hello everyone!🌙 {TARGET_USERNAME} is now LIVE!!\n"
                                f"Come hangout! 🖤\n"
                                f"👉 https://www.tiktok.com/@{TARGET_USERNAME}\n"
                                f"👉 https://twitch.tv/{TARGET_USERNAME}"
                            )

                was_live = is_live
                await asyncio.sleep(60)

            except Exception as e:
                print(f"[Stream] Error: {e}")
                await asyncio.sleep(60)

###################################
#
#  PRIVATE FUNCTIONS
#
###################################

async def get_twitch_token():
    """
    Gets a fresh twitch app access token for twitch api calls
    """

    URL_TWITCH_TOKEN = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(URL_TWITCH_TOKEN, params=params) as resp:
            data = await resp.json()
            return data["access_token"]


async def check_twitch_live(session, token):
    """
    Checks if TARGET_USERNAME is currently live on Twitch.
    """
    url = f"https://api.twitch.tv/helix/streams?user_login={TARGET_USERNAME}"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {token}"
    }

    async with session.get(url, headers=headers) as resp:
        if resp.status != 200:
            print(f"Error from Twitch API: {resp.status}")
            return False
        data = await resp.json()
        streams = data.get("data", [])
        return bool(streams)

async def check_tiktok_live(session):
    """
    Checks if TARGET_USERNAME is currently live on TikTok.
    This scrapes the TikTok profile page and looks for the LIVE badge.
    """
    url = f"https://www.tiktok.com/@{TARGET_USERNAME}"

    headers = {
        "User-Agent": "Mozilla/5.0",  # TikTok rejects empty/default user agents
    }

    async with session.get(url, headers=headers) as resp:
        if resp.status != 200:
            print(f"Error fetching TikTok page: {resp.status}")
            return False

        html = await resp.text()

        # look for the LIVE badge text
        if "LIVE</span>" in html or "LIVE" in html:
            return True

        return False

