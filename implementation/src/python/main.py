import discord
import logging
from modules import check_health
from modules import onboarding
from modules import notify_starting_stream

# disable gateway logging while debugging
logging.getLogger("discord.gateway").setLevel(logging.ERROR)

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)

# track if we already registered modules
modules_registered = False

if __name__ == "__main__":
    with open("../../../discord_bot_token") as f:
        TOKEN = f.read().strip()

    async def setup_guilds():
        global modules_registered

        if not client.guilds:
            print("Bot is not in any servers yet. Invite it to a server to begin.")
            return

        failed_guilds = []
        for guild in client.guilds:
            ok = await check_health.run_health_check(guild, client.user)
            if not ok:
                print(f"❌ Health check failed on {guild.name}")
                failed_guilds.append(guild.name)

        if failed_guilds:
            print(f"Some guilds failed health check: {failed_guilds}")
        else:
            print("All guilds passed health check.")

        if not modules_registered:
            print("Starting other client modules...")
            onboarding.register(client)
            notify_starting_stream.register(client)
            modules_registered = True

    @client.event
    async def on_ready():
        print(f"Logged in as {client.user} in {[g.name for g in client.guilds]}")
        await setup_guilds()

    @client.event
    async def on_guild_join(guild):
        print(f"📥 Bot was invited to a new guild: {guild.name}")
        ok = await check_health.run_health_check(guild, client.user)
        if not ok:
            print(f"❌ Health check failed on {guild.name}. Leaving guild.")
            await guild.leave()
            return

        print(f"Health check passed on {guild.name}.")

        if not modules_registered:
            print("Registering modules after first successful guild.")
            onboarding.register(client)
            notify_starting_stream.register(client)

    client.run(TOKEN)
