# telegram-support-bot

Simple, easy to use, Telegram bot to hide your identity. Useful for support, anonymous channel management. Free clone of Livegram Bot.

## How this bot works

1. User writes a message to your bot
2. Bot forwards the message to your support chat (with only you or with your support team for example)
3. Any support chat participant can reply to a forwarded message
4. Bot will copy the message and send it to user

If user disabled forwarding his username with messages (in TG privacy settings), bot would send message with user ID to support chat after user's forwarded message. Support team should reply to this message, not forwarded message. That's a technical limitation by telegram and there is not much we can do about it

## Difference between this fork and upstream projects

* (stateful only) Ability to ban users.
* (stateful only) Ability to delete messages from support side.
* (stateful only) Ratelimiting (warns user first, next time bans) that bans spammers. 
* Moved strings from .env to `settings.py` (so we could include them in git log).
* Made sending a message to support optional and configurable when a user clicks `/start`.
* Fixed exploit related to forwarding already forwarded messages from users; forbid the bot from forwarding forwarded messages.
* The bot now sets a reaction to successfully forwarded messages (on the support side only).
* Added advanced formatting for all strings using Telegram HTML syntax.
* Added a configurable option to forbid users from sending voice and round video messages.
* Added an alert for user side indicating that replies are not forwarded, only the content of the message.

## Stateful vs stateless version

There exists two versions of this bot, stateful and stateless. Stateful is more feature rich, but it stores data for ratelimiting (timestamps and user ID's) in memory and requires persistent storage for list of banned users

Stateless doesn't need any persistent storage, it doesn't store anything at all (even in memory), hence the name

## Features (stateful only)

Available commands (only through support chat, users have no access to them):

- /ban
- /unban
- /quietban
- /banlist — Shows all banned users
- /delete — Deletes message sent by support from user's chat (can be deleted only 48hrs after sending — telegram technical limitation)

Ban-related commands usage:

```
/[ban | quietban | unban] [<user_id> | reply to message] [<reason>]

Where:
- <user_id>: The ID of the user to ban
- reply to message: You can reply to a user's message or to bot's message with user's ID as described above.
- <reason>: (Optional) The reason for banning the user (displayed in banlist). Ignored by /unban

Example:
/ban 5268501992 Spam
Or (by replying to a user's message)
/ban Spam
```

`/banlist` returns:

```
ID: 858508111
      2025-05-05 03:51:15
      Spam
ID: 2543238746
      2025-05-05 03:50:58
      Spam!
ID: 283749746
      2025-05-05 03:40:54
      The user was banned after exceeding the rate limit of 6 messages in 10 seconds. The user was warned after their 4th message(s) and still continued to spam.
```

Bot embeds clickable links to users in ID strings if user who's ID bot is tried to embed had already interacted with bot

`/delete` usage
```
When using the /delete command, you must reply to the operator's message that you wish to delete
```

Bot reacts with different reaction to messages, that had been successfully deleted (🙈 by default, configurable in `settings.py`)

## .env variables

You need to specify these env variables to run this bot. If you run it locally, you can also write them in `.env` text file.

``` bash
TELEGRAM_TOKEN=12345678:longstringofletterslonglonglong # your bot's token
TELEGRAM_SUPPORT_CHAT_ID=-9876543210 # chat_id where the bot will forward all incoming messages. 

# You can enable "Show Peer IDs in Profile" settings in Telegram Desktop and look in the chat description to get ID. Settings -> Advanced -> scroll down -> Experimental 
# Also, you can use https://t.me/ShowJsonBot to find it's chat_id.
```

## Run bot locally

1. Select stateful or stateless version, clone the repo and checkout `stateless` branch if you want to run the stateless version. `stateful` branch is the default one, that would be checked-out immediately after the clone

2. Create python virtual environment (optional)

3. Install all dependencies:

```bash
pip install -r requirements.txt
```

4. Configure .env file

5. (optional) Change strings or tweak settings (there is a lot) in `settings.py` file

5. Run the bot:

``` bash
python main.py
```

## Authors

This is a fork of [rus-ai's fork](https://github.com/rus-ai/telegram-support-bot) of [ohld's telegram-support-bot](https://github.com/ohld/telegram-support-bot)

Thanks to all contributors of this and upstream projects
