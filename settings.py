import os
from dotenv import load_dotenv, find_dotenv
from telegram import User, constants

load_dotenv(find_dotenv())

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if TELEGRAM_TOKEN is None:
    raise Exception("Please setup the .env variable TELEGRAM_TOKEN.")

TELEGRAM_SUPPORT_CHAT_ID = os.getenv("TELEGRAM_SUPPORT_CHAT_ID")
if TELEGRAM_SUPPORT_CHAT_ID is None or not str(TELEGRAM_SUPPORT_CHAT_ID).lstrip("-").isdigit():
    raise Exception("You need to specify 'TELEGRAM_SUPPORT_CHAT_ID' env variable: The bot will forward all messages to this chat_id. Add this bot https://t.me/ShowJsonBot to your private chat to find its chat_id.")
TELEGRAM_SUPPORT_CHAT_ID = int(TELEGRAM_SUPPORT_CHAT_ID)



            ###########
            # Strings #
            ###########

# How to style messages (bold, italic): 
# https://core.telegram.org/api/entities
# https://core.telegram.org/type/MessageEntity
#
# Bot uses ` parse_mode='HTML' `


# Translation guide:
# Copy-paste this file in any decent LLM and ask it to translate every string to your language of choice

# text of a message that bot will write to user on /start command
USER_SIDE__WELCOME_MESSAGE = """
Привет! Через этого бота вы можете связаться с администрацией

Отправьте своё сообщение и бот автоматически перенаправит его администрации

Поддерживаются любые типы вложений (картинки, стикеры и т.д.) в обе стороны, кроме голосовых и видеосообщений (кружков). Не поддерживается пересылка уже пересланных сообщений от других пользователей, ответов, а так же реакций на сообщения
"""


# If user doesn't allow forwarding of their messages, the bot adds a comment with the user's ID for the reply
# The support team must reply to the "bot reply," not to the original user's forwarded message
SUPPORT_SIDE__REPLY_TO_THIS_MESSAGE = "💬 Чтобы ответить автору 👆 сообщения выше, твой ответ должен быть на сообщение бота (вот это вот что ты сейчас читаешь)"
SUPPORT_SIDE__WRONG_REPLY = f"""
❌ Вы или ответили на неправильное сообщение, или у пользователя выше была включена опция скрытия аккаунта при пересылке сообщений. Чтобы пользователю был переслан ваш ответ, отвечайте на сообщение бота под пересланными сообщениями пользователя

С помощью поиска в телеграм, поищите ближайшее сообщение с текстом
\"{SUPPORT_SIDE__REPLY_TO_THIS_MESSAGE}\""
"""


# Bot doesn't support forwarded messages on purpose. Basically a band-aid fix to exploit, to keep the bot simple and stateless
SUPPORT_SIDE__USER_TRIED_FORWARDING_MESSAGE = '⚠ Пользователь попытался переслать сообщение, бот сообщил ему, что это не поддерживается\n\nВы можете написать ответ пользователю, ответив на это сообщение'
USER_SIDE__FORWARDS_ARE_NOT_SUPPORTED = """
⚠ Пересланные сообщения не поддерживаются ботом.

Сообщение было проигнорировано и операторы его не получили. Вы можете пересланные сообщения скриншотом"""

SUPPORT_SIDE__SOMETHING_WENT_WRONG = "Что-то пошло не так, сообщение не было переслано"


# Bot doesn't support forwarding replies
USER_SIDE__REPLIES_ARE_NOT_SUPPORTED = """
⚠ Ответы на сообщения не поддерживаются ботом.

Ответ был проигнорирован при пересылке, операторы получили сообщение, но без контекста в виде ответа"""


FORBID_USERS_TO_SEND_VOICE_AND_VIDEO_MESSAGES = True
USER_SIDE__VOICE_AND_VIDEO_MESSAGES_FORBIDDEN = """
⚠ Пересылка голосовых и видео сообщений не поддерживается ботом. <span class="tg-spoiler">Из принципа</span>
"""


# Available reaction emojis are stored in `telegram.constants.ReactionEmoji` enum
SUPPORT_SIDE__REACTION_MESSAGE_SUCCESSFULLY_FORWARDED = constants.ReactionEmoji.OK_HAND_SIGN


SEND_USER_STARTED_CHAT_MSG_TO_SUPPORT_SIDE = False

"""
`user_info` object example:
{
    'is_bot': False,
    'username': 'username_blahblah',
    'first_name': 'John',
    'last_name': 'Doe'
    'id': 5121488762,
    'language_code': 'en'
}.
"""
def SUPPORT_SIDE__user_started_chat(user_info: User, chat_info) -> str:
    return f"""
Пользователь начал чат с ботом:
<a href="tg://user?id={user_info.id}">{user_info.first_name} {user_info.last_name}</a>
@{user_info.username if user_info.username != "" else "нет юзернейма"}
ID пользователя: {user_info.id}
{chat_info}
"""


SUPPORT_SIDE__COMMAND__BAN_USAGE = "SUPPORT_SIDE__COMMAND__BAN_USAGE"
SUPPORT_SIDE__COMMAND__BAN_SUCCESSFUL = "SUPPORT_SIDE__COMMAND__BAN_SUCCESSFUL"
SUPPORT_SIDE__COMMAND__UNBAN_SUCCESSFUL = "SUPPORT_SIDE__COMMAND__UNBAN_SUCCESSFUL"

DEFAULT_BAN_REASON = "DEFAULT_BAN_REASON"
