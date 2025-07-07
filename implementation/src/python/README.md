# How to Develop this in Python

## Virtual Environment
First we want to develop in a venv for isolation.
1. `python3 -m venv venv`
2. `source ~/Repos/discord_welcome_bot/implementation/src/python/venv/bin/activate`

## Install Dependencies
Okay now we install discord.
1. `pip install -U discord.py`

## Database
Read database: `sqlite3 ~/Repos/discord_welcome_bot/implementation/src/python/data/onboarding.db`
Or with GUI `sqlitebrowser ~/Repos/discord_welcome_bot/implementation/src/python/data/onboarding.db &`
