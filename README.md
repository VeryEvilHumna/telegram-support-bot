# telegram-support-bot

Simple, easy to use, stateless Telegram bot to hide your identity. Useful for support, anonymous channel management. Free clone of Livegram Bot.

## How bot works

1. User writes a message to your bot
2. Bot forwards the message to your support chat (with only you or with your support team for example)
3. Any support chat participant can reply to a forwarded message
4. Bot will copy the message and send it to user

If user disabled forwarding his username with messages (in TG privacy settings), bot would send message with user ID to support chat after user's forwarded message. Support team should reply to this message, not forwarded message. That's a technical limitation by telegram and there is not much we can do about it

## .env variables

You need to specify these env variables to run this bot. If you run it locally, you can also write them in `.env` text file.

``` bash
TELEGRAM_TOKEN=12345678:longstringofletterslonglonglong # your bot's token
TELEGRAM_SUPPORT_CHAT_ID=-9876543210 # chat_id where the bot will forward all incoming messages. 

# You can enable "Show Peer IDs in Profile" settings in Telegram Desktop and look in the chat description to get ID. Settings -> Advanced -> scroll down -> Experimental 
# Also, you can use https://t.me/ShowJsonBot to find it's chat_id.
```

## Run bot locally

1. Create virtual environment (optional) 

2. Install all dependencies:

```bash
pip install -r requirements.txt
```

3. Configure .env file

4. (optional) Change strings or tweak settings in `settings.py` file

6. Run the bot:

``` bash
python main.py
```
