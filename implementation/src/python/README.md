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

## Debugging

Run: `python3 -m pdb welcome_bot.py` or ``python3 -m pudb welcome_bot.py``

## File Structure

```
.
├── data
│   └── onboarding.db
├── db
│   ├── onboarding_db.py
│   └── __pycache__
│       └── onboarding_db.cpython-313.pyc
├── images
│   ├── lore_users
│   │   ├── lore__skypeisbetter_222483568759144449.png
│   │   └── subphoto_users
│   │       ├── photo_222483568759144449.jpg
│   │       └── photo_222483568759144449.png
│   └── MyLoreTemplate.png
├── main.py
├── modules
│   ├── __init__.py
│   ├── lore_image.py
│   ├── onboarding.py
│   ├── __pycache__
│   │   ├── __init__.cpython-313.pyc
│   │   ├── lore_image.cpython-313.pyc
│   │   └── onboarding.cpython-313.pyc
│   └── README.md
└── README.md

9 directories, 16 files
```

main.py is the entry point of the bot. It initializes the client, sets up intents, registers the modules, and runs the bot from the token.

Each module attaches event listeners to the Discord client.

