# About this Project

Streamer girl wants me to create a discord bot for her. This bot will all things general in this server.

### Discord and Bot settings

When creating the bot discord get bot token and enable `Server Members Intent`

To invite the bot to a server, set it up by going to developer dashboard, OAUTH2 URL Generator, check bot. Then check these following permissions for bot:

* Read Messages/View Channels
* Send Messages
* Read Message History
* Mention Everyone
* Manage Roles

Also bot needs to be able to view and manage channels

Then just copy the generated URL and paste it into browser. This should bring up discord and we can add the bot to our chosen server.

In the discord settings we need to create channel category Onboarding and create Unverified role, add everyone to that role.

Make introduction channel invisible to unverified, then we remove unverified role after they complete bot.

## Development and Tools

1. Discord developer account
2. Developed in Linux environment
3. Python is easiest - but I want to do C++ to manually manage websockets, etc.
