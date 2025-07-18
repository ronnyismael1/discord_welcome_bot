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

# register all feature modules here
# check_health.register(client)
# onboarding.register(client)
# notify_starting_stream.register(client)

if __name__ == "__main__":
    with open("../../../discord_bot_token") as f:
        TOKEN = f.read().strip()

    @client.event
    async def on_ready():
        print(f"Logged in as {client.user} in {[g.name for g in client.guilds]}")

        ok = await check_health.run(client)
        if not ok:
            print("Health check failed. Shutting down.")
            await client.close()
            return

        print("Starting other client modules...")

        # Only register other modules after health passes
        onboarding.register(client)
        notify_starting_stream.register(client)

    client.run(TOKEN)
