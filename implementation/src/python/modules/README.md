# Different Modules that this Bot Supports

1. User Onboarding
2. Live Notification

## User Onboarding

### Requirements
1. On someone joining the server, bot needs to greet and prompt with responses.

### Workflow
1. Person joins server, bot sees there's new person either from watching the welcome channel or some other API.
2. Bot will send them a message in a private new thread maybe called #start-here, and also send message to private bot channel notifying admins that it successfully detected new user and prompted them.
3. The private thread will say hello, and then begin to prompt them with questionnaire
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
7. Favorite show:let g:autoformat = v:false
8. Favorite song
9. Hobbies
10. Photo that describes you: [user insert photo]

## Live Notification

### Requirements
1. Whenever gloomxmoon goes live, we need the bot to send a message to the #Announcements channel.

### Setup
*TWITCH API*
1. Log into Twitch Developer Console and then click "Register Your Application"
2. 

