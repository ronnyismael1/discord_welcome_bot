# About this Project

Streamer girl wants me to create a discord bot for her. This bot will welcome people and prompt them to introduce themselves.

## Workflow
1. Person joins server, bot sees there's new person either from watching the welcome channel or some other API.
2. Bot will send private DM to new person, and also send message to private bot channel notifying admins that it successfully detected new user and prompted them.
3. The private DM will say hello, and then begin to prompt them with questionnaire
4. New person will respond to questionnaire and the bot will record their answers
5. The bot will take their answers and create them a custom "My Lore" image
6. Bot will send the image to the user and tell them to post it in the introduction channel
    - ORRRRR will post it and tag the user

### Questionnaire 
1. My name is ____.
2. Pronouns _____.
3. Fun Fact About You
4. Quote: "_____".
5. Zodiac Sign
6. Top 3 games
7. Favorite show
8. Favorite song
9. Hobbies
10. Photo that describes you: [user insert photo]

## Requirements
1. On someone joining the server, bot needs to greet and prompt with responses.
2. This bot needs to be hosted locally, maybe on RASPI or on computer.
3. ???

### Bot settings
When creating the bot discord get bot token and enable `Server Members Intent`

To invite the bot to a server, set it up by going to developer dashboard, OAUTH2 URL Generator, check bot. Then check these following permissions for bot:
* Read Messages/View Channels
* Send Messages
* Read Message History
* Mention Everyone 
* Manage Roles

Then just copy the generated URL and paste it into browser. This should bring up discord and we can add the bot to our chosen server.


## Development and Tools
1. Discord developer account
2. Developed in Linux environment
3. Python is easiest - but I want to do C++ to manually manage websockets, etc. 

