import html
import os
from dotenv import load_dotenv, find_dotenv
from telegram import User, constants, Update

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


SUPPORT_SIDE__COMMAND__BAN_USAGE = html.escape("""
Использование: /[ban | quietban] [<user_id> | ответ на сообщение] [<причина>]

Где:
- <user_id>: ID пользователя, которого нужно заблокировать
- ответ на сообщение: Вы можете ответить на сообщение пользователя, чтобы заблокировать его без указания ID.
- <причина>: (Необязательная) причина блокировки пользователя (отображается только в банлисте)

Пример:
/ban 5268501992 Спам
Или (ответив на сообщение пользователя)
/ban Спам
""")

SUPPORT_SIDE__COMMAND__LOUDBAN_SUCCESSFUL = "🚩 Пользователь был успешно заблокирован и уведомлён об этом"
SUPPORT_SIDE__COMMAND__QUIETBAN_SUCCESSFUL = "🤫 Пользователь был успешно заблокирован без уведомления о бане"
SUPPORT_SIDE__COMMAND__UNBAN_SUCCESSFUL = "🕊️ Пользователь был успешно разблокирован"

USER_SIDE__LOUDBAN_BANNED_BY_SUPPORT = """
🚩 <b>Вы были заблокированы администрацией!</b>

Бот перестанет реагировать на ваши сообщения, они не будут переадресованы администрации. Обжаловать это решение нельзя.
"""

DEFAULT_BAN_REASON = "Причина бана не была указана"


# Allow user to send RATELIMIT_BAN_AFTER_THIS_MANY_MESSAGES_IN_WINDOW messages 
# in RATELIMIT_TIME_WINDOW_SEC seconds, ban user if user sends
# more messages in RATELIMIT_TIME_WINDOW_SEC seconds
RATELIMIT_BAN_AFTER_THIS_MANY_MESSAGES_IN_WINDOW = 8
RATELIMIT_WARN_AFTER_THIS_MANY_MESSAGES_IN_WINDOW = 5
RATELIMIT_TIME_WINDOW_SEC = 30

USER_SIDE__RATELIMIT_WARN_MESSAGE = """
⚠️ <b>Стоп стоп стоп!</b>

Спам в бота никак не ускорит ответ администрации. Если вы продолжите спамить, бот автоматически вас забанит, <b>без возможности обжаловать это решение</b>
"""

USER_SIDE__RATELIMIT_BAN_MESSAGE = """
🚩 Бан! Бот вас предупредил, но вы всё равно продолжили отправлять сообщения слишком быстро

Бот больше не будет реагировать на ваши сообщения и пересылать их администрации
"""

def SUPPORT_SIDE__ratelimit_ban_message(update: Update) -> str:
    return f"""
🤡 Пользователь <a href="tg://user?id={update.effective_user.id}">{update.effective_user.first_name} {update.effective_user.last_name}</a> @{update.effective_user.username if update.effective_user.username != "" else "нет юзернейма"}. ID: {update.effective_user.id}
был забанен после превышения рейтлимита {RATELIMIT_BAN_AFTER_THIS_MANY_MESSAGES_IN_WINDOW + 1} сообщений за {RATELIMIT_TIME_WINDOW_SEC} секунд.

Пользователь был предупреждён после его {RATELIMIT_WARN_AFTER_THIS_MANY_MESSAGES_IN_WINDOW + 1} сообщений(ия) и всё равно продолжил спамить
"""

def ratelimit_ban_reason():
    return f"""Пользователь был забанен после превышения рейтлимита {RATELIMIT_BAN_AFTER_THIS_MANY_MESSAGES_IN_WINDOW + 1} сообщений за {RATELIMIT_TIME_WINDOW_SEC} секунд. Пользователь был предупреждён после его {RATELIMIT_WARN_AFTER_THIS_MANY_MESSAGES_IN_WINDOW + 1} сообщений(ия) и всё равно продолжил спамить"""
