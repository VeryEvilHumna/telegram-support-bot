import asyncio
from asyncio.log import logger
from functools import wraps
import html
import json
import os
import time
import traceback
from telegram import Chat, Update
from telegram.error import BadRequest
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, Application
import dbm
from typing import Callable
from datetime import datetime
import schedule 

import settings

os.makedirs("data", exist_ok=True)

banned_db = dbm.open(file="data/banned.dbm", flag="c")
BANNED_STR = "b"

banlist_db = dbm.open(file="data/banlist.dbm", flag="c")

smtoum_db = dbm.open(file="data/support_messages_to_user_messages_map.dbm", flag="c")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(settings.USER_SIDE__WELCOME_MESSAGE)

    if settings.SEND_USER_STARTED_CHAT_MSG_TO_SUPPORT_SIDE:
        user_info = update.message.from_user
        chat_info = ""
        if update.message.chat.type != Chat.PRIVATE:
            chat_info = f"\n\nChat{update.message.chat.to_dict()}"

        print("User started chat with a bot:", user_info)

        await context.bot.send_message(
            chat_id=settings.TELEGRAM_SUPPORT_CHAT_ID,
            parse_mode='HTML',
            text=settings.SUPPORT_SIDE__user_started_chat(user_info, chat_info)
        )


def if_truthful_else_nothing(expr: str, prepend: str) -> str:
    return (prepend + expr) if expr else ""


async def forward_to_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """{ 
        'message_id': 5, 
        'date': 1605106546, 
        'chat': {'id': 49820636, 'type': 'private', 'username': 'danokhlopkov', 'first_name': 'Daniil', 'last_name': 'Okhlopkov'}, 
        'text': 'TEST QOO', 'entities': [], 'caption_entities': [], 'photo': [], 'new_chat_members': [], 'new_chat_photo': [], 'delete_chat_photo': False, 'group_chat_created': False, 'supergroup_chat_created': False, 'channel_chat_created': False, 
        'from': {'id': 49820636, 'first_name': 'Daniil', 'is_bot': False, 'last_name': 'Okhlopkov', 'username': 'danokhlopkov', 'language_code': 'en'}
    }"""
    
    if settings.FORBID_USERS_TO_SEND_VOICE_AND_VIDEO_MESSAGES and (update.message.voice is not None or update.message.video_note is not None):
        await context.bot.send_message(
            chat_id=update.message.chat.id,
            parse_mode='HTML',
            text=settings.USER_SIDE__VOICE_AND_VIDEO_MESSAGES_FORBIDDEN
        )
        return
    
    if update.message.forward_from is not None:
        future1 = context.bot.send_message(
            chat_id=update.message.chat.id,
            reply_to_message_id=update.message.message_id,
            text=settings.USER_SIDE__FORWARDS_ARE_NOT_SUPPORTED,
        )
        future2 = context.bot.send_message(
            chat_id=settings.TELEGRAM_SUPPORT_CHAT_ID,
            parse_mode='HTML',
            text=f'{update.message.from_user.id} {if_truthful_else_nothing(update.message.from_user.username, "@")}\n\n{settings.SUPPORT_SIDE__USER_TRIED_FORWARDING_MESSAGE}'
        )
        asyncio.gather(future1, future2)
        return

    if update.message.reply_to_message is not None:
        await context.bot.send_message(
            chat_id=update.message.chat.id,
            reply_to_message_id=update.message.message_id,
            text=settings.USER_SIDE__REPLIES_ARE_NOT_SUPPORTED,
            parse_mode='HTML'
        )
        
    forwarded = await update.message.forward(chat_id=settings.TELEGRAM_SUPPORT_CHAT_ID)
    if not forwarded.forward_from:
        await context.bot.send_message(
            chat_id=settings.TELEGRAM_SUPPORT_CHAT_ID,
            parse_mode='HTML',
            reply_to_message_id=forwarded.message_id,
            text=f'{update.message.from_user.id} {if_truthful_else_nothing(update.message.from_user.username, "@")}\n\n{settings.SUPPORT_SIDE__REPLY_TO_THIS_MESSAGE}'
        )


async def forward_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """{
        'message_id': 10, 'date': 1605106662, 
        'chat': {'id': -484179205, 'type': 'group', 'title': '☎️ SUPPORT CHAT', 'all_members_are_administrators': True}, 
        'reply_to_message': {
            'message_id': 9, 'date': 1605106659, 
            'chat': {'id': -484179205, 'type': 'group', 'title': '☎️ SUPPORT CHAT', 'all_members_are_administrators': True}, 
            'forward_from': {'id': 49820636, 'first_name': 'Daniil', 'is_bot': False, 'last_name': 'Okhlopkov', 'danokhlopkov': 'okhlopkov', 'language_code': 'en'}, 
            'forward_date': 1605106658, 
            'text': 'g', 'entities': [], 'caption_entities': [], 'photo': [], 'new_chat_members': [], 'new_chat_photo': [], 
            'delete_chat_photo': False, 'group_chat_created': False, 'supergroup_chat_created': False, 'channel_chat_created': False, 
            'from': {'id': 1440913096, 'first_name': 'SUPPORT', 'is_bot': True, 'username': 'lolkek'}
        }, 
        'text': 'ggg', 'entities': [], 'caption_entities': [], 'photo': [], 'new_chat_members': [], 'new_chat_photo': [], 'delete_chat_photo': False, 
        'group_chat_created': False, 'supergroup_chat_created': False, 'channel_chat_created': False, 
        'from': {'id': 49820636, 'first_name': 'Daniil', 'is_bot': False, 'last_name': 'Okhlopkov', 'username': 'danokhlopkov', 'language_code': 'en'}
    }"""
    if update.message.reply_to_message.from_user.id == context.bot.id:
        user_id = get_user_id(update)
        if user_id:
            message_id = await context.bot.copy_message(
                message_id=update.message.message_id,
                chat_id=user_id,
                from_chat_id=update.message.chat_id
            )
            if message_id is not None:    
                await context.bot.set_message_reaction(
                    chat_id=update.message.chat_id,
                    message_id=update.message.message_id,
                    reaction=settings.SUPPORT_SIDE__REACTION_MESSAGE_SUCCESSFULLY_FORWARDED
                )
                # Save message mapping so we can delete it later
                smtoum_db[str(update.effective_message.id)] = f"{str(user_id)},{str(message_id.message_id)}"
                # Reset ratelimits
                timestamps_of_last_messages[update.effective_user.id].clear()
            else:
                await context.bot.send_message(
                    chat_id=settings.TELEGRAM_SUPPORT_CHAT_ID,
                    text=settings.SUPPORT_SIDE__SOMETHING_WENT_WRONG,
                    parse_mode='HTML'
                )
                
        else:
            await context.bot.send_message(
                chat_id=settings.TELEGRAM_SUPPORT_CHAT_ID,
                text=settings.SUPPORT_SIDE__WRONG_REPLY,
                parse_mode='HTML'
            )

def get_user_id(update: Update):
    user_id = None
    if update.message.reply_to_message.forward_from:
        user_id = update.message.reply_to_message.forward_from.id
    elif update.message.reply_to_message.text and settings.SUPPORT_SIDE__REPLY_TO_THIS_MESSAGE in update.message.reply_to_message.text or settings.SUPPORT_SIDE__USER_TRIED_FORWARDING_MESSAGE in update.message.reply_to_message.text:
        try:
            user_id = int(update.message.reply_to_message.text.split(' ')[0])
        except ValueError:
            user_id = None
    return user_id



def ban(user_id: int, reason: str):
    banned_db[str(user_id)] = BANNED_STR
    banlist_db[str(user_id)] = datetime.now().replace(microsecond=0).isoformat().replace("T", " ") + "\n      " + reason

def unban(user_id: int):
    banned_db.pop(str(user_id))
    banlist_db.pop(str(user_id))
    
def is_banned(user_id: int):
    if banned_db.get(str(user_id)) is not None:
        return banned_db.get(str(user_id)).decode() == BANNED_STR
    else:
        return False

def get_banlist():
    banlist = ""
    
    for key, value in banlist_db.items():
        try:
            banlist += 'ID: ' + f'<a href="tg://user?id={key.decode()}">' + key.decode() + "</a>\n      " + value.decode() + "\n"
        except UnicodeDecodeError:
                        banlist += 'ID: ' + f'<a href="tg://user?id={key.decode()}">' + key.decode() + "</a>\n      (Failed to decode)" + str(value) + "\n"
    return banlist if banlist.__len__() != 0 else settings.SUPPORT_SIDE__EMPTY_BANLIST
    
    
# returns user_id on successful ban
async def base_ban_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = 0
    if len(context.args) >= 1 and context.args[0].isdigit():
        user_id = context.args[0]
        reason = ban_reason_from_args(update, context, True)
        ban(user_id, reason)
        return user_id
        
    elif update.message.reply_to_message is not None:
        user_id = get_user_id(update)
        if user_id is not None:
            reason = ban_reason_from_args(update, context, False)
            ban(user_id, reason)
            return user_id
        else:
            await context.bot.send_message(
                chat_id=settings.TELEGRAM_SUPPORT_CHAT_ID,
                text=settings.SUPPORT_SIDE__WRONG_REPLY,
                parse_mode='HTML'
            )
            return
    else:
        await context.bot.send_message(
            chat_id=settings.TELEGRAM_SUPPORT_CHAT_ID,
            text=settings.SUPPORT_SIDE__COMMAND__BAN_USAGE,
            parse_mode='HTML'
        )
        return



def ban_reason_from_args(update: Update, context: ContextTypes.DEFAULT_TYPE, id_is_in_args: bool):
    reason = ''
    if len(context.args) > 1:
        reason_array = update.effective_message.text.split(" ")    
        del reason_array[0]
        if id_is_in_args:
            del reason_array[0]
        reason = ' '.join(reason_array)
    else:
        reason = settings.DEFAULT_BAN_REASON
    return reason



async def unban_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = 0
    if len(context.args) == 1 and context.args[0].isdigit():
        user_id = context.args[0]
        unban(user_id)
    elif update.message.reply_to_message is not None:
        user_id = get_user_id(update)
        if user_id is not None:
            unban(user_id)
        else:
            await context.bot.send_message(
                chat_id=settings.TELEGRAM_SUPPORT_CHAT_ID,
                text=settings.SUPPORT_SIDE__WRONG_REPLY,
                parse_mode='HTML'
            )
            return
    else:
        await context.bot.send_message(
            chat_id=settings.TELEGRAM_SUPPORT_CHAT_ID,
            text=settings.SUPPORT_SIDE__COMMAND__BAN_USAGE,
            parse_mode='HTML'
        )
        return
    
    await context.bot.send_message(
        chat_id=settings.TELEGRAM_SUPPORT_CHAT_ID,
        text=settings.SUPPORT_SIDE__COMMAND__UNBAN_SUCCESSFUL,
        parse_mode='HTML'
    )

async def banlist_callback(update: object, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=settings.TELEGRAM_SUPPORT_CHAT_ID,
        text=get_banlist(),
        parse_mode='HTML'
    )



timestamps_of_last_messages: dict[int, list[float]] = {}

async def middleware(callback: Callable) -> Callable:
    @wraps(callback)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Callable:
        # 1. Ignore requests from banned users
        if is_banned(update.effective_user.id):
            return
        
        # 2. Rate limiting
        schedule.run_pending()
        
        if timestamps_of_last_messages.get(update.effective_user.id) is None:
            timestamps_of_last_messages[update.effective_user.id] = [time.time()]
        else:
            timestamps_of_last_messages.get(update.effective_user.id).append(time.time())
        
        messages_in_window = 0
        now_minus_window_time = time.time() - settings.RATELIMIT_TIME_WINDOW_SEC
        for ts in timestamps_of_last_messages[update.effective_user.id]:
            if now_minus_window_time < ts:
                messages_in_window +=1

        if messages_in_window >= settings.RATELIMIT_WARN_AFTER_THIS_MANY_MESSAGES_IN_WINDOW:
            await context.bot.send_message(
                    chat_id=update.message.chat.id,
                    parse_mode='HTML',
                    text=settings.USER_SIDE__RATELIMIT_WARN_MESSAGE
            )
        if messages_in_window >= settings.RATELIMIT_BAN_AFTER_THIS_MANY_MESSAGES_IN_WINDOW:
            print(f"User {update.effective_user.id}, @{update.effective_user.username}: {update.effective_user.first_name} {update.effective_user.last_name} has been banned for reaching the ratelimit")
            ban(update.effective_user.id, settings.ratelimit_ban_reason())
            future1 = context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    parse_mode='HTML',
                    text=settings.USER_SIDE__RATELIMIT_BAN_MESSAGE
            )
            future2 = context.bot.send_message(
                    chat_id=settings.TELEGRAM_SUPPORT_CHAT_ID,
                    parse_mode='HTML',
                    text=settings.SUPPORT_SIDE__ratelimit_ban_message(update)
            )
            
            await asyncio.gather(future1, future2)
            return
            
        return await callback(update, context)
    
    return wrapper
    
    
    
async def loudban_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = await base_ban_callback(update, context)
    if user_id:
        await context.bot.send_message(
            chat_id=user_id,
            parse_mode='HTML',
            text=settings.USER_SIDE__LOUDBAN_BANNED_BY_SUPPORT
        )
        await context.bot.send_message(
            chat_id=settings.TELEGRAM_SUPPORT_CHAT_ID,
            parse_mode='HTML',
            text=settings.SUPPORT_SIDE__COMMAND__LOUDBAN_SUCCESSFUL
        )
    
async def quietban_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = await base_ban_callback(update, context)
    if user_id:
        await context.bot.send_message(
            chat_id=settings.TELEGRAM_SUPPORT_CHAT_ID,
            parse_mode='HTML',
            text=settings.SUPPORT_SIDE__COMMAND__QUIETBAN_SUCCESSFUL
        )


    
# copy-pasted from https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/errorhandlerbot.py
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error("Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        "An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    await context.bot.send_message(
        chat_id=settings.TELEGRAM_SUPPORT_CHAT_ID, text=message, parse_mode='HTML'
    )



async def delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message is not None:
        data_bytes = smtoum_db.get(str(update.message.reply_to_message.id))
        
        if data_bytes:
            chat_id, user_side_msg_id = data_bytes.decode().split(",")
            isDeleted = False
            try:
                isDeleted = await context.bot.delete_message(
                    message_id=int(user_side_msg_id),
                    chat_id=int(chat_id)
                )
            except BadRequest:
                isDeleted = False
            if isDeleted:
                await context.bot.send_message(
                    chat_id=settings.TELEGRAM_SUPPORT_CHAT_ID,
                    parse_mode='HTML',
                    text=settings.SUPPORT_SIDE__COMMAND__DELETE_SUCCESSFUL
                )
                await context.bot.set_message_reaction(
                    chat_id=settings.TELEGRAM_SUPPORT_CHAT_ID,
                    message_id=update.message.reply_to_message.id,
                    reaction=settings.SUPPORT_SIDE__REACTION_MESSAGE_SUCCESSFULLY_DELETED,
                    is_big=True
                )
                return
        await context.bot.send_message(
            chat_id=settings.TELEGRAM_SUPPORT_CHAT_ID,
            parse_mode='HTML',
            text=settings.SUPPORT_SIDE__COMMAND__DELETE_ERROR
        )
    else:
        await context.bot.send_message(
            chat_id=settings.TELEGRAM_SUPPORT_CHAT_ID,
            parse_mode='HTML',
            text=settings.SUPPORT_SIDE__COMMAND__DELETE_USAGE
        )

        
        

def ratelimit_cleanup():
    for user_id, marr in timestamps_of_last_messages.items():
        for i, ts in enumerate(marr):
            if time.time() - settings.RATELIMIT_TIME_WINDOW_SEC > ts:
                del marr[i]


async def setup_dispatcher(app: Application):
    app.add_handler(CommandHandler('start', await middleware(start)))
    app.add_handler(CommandHandler("quietban", filters=filters.Chat(settings.TELEGRAM_SUPPORT_CHAT_ID), callback=quietban_callback))
    app.add_handler(CommandHandler("ban", filters=filters.Chat(settings.TELEGRAM_SUPPORT_CHAT_ID), callback=loudban_callback))
    app.add_handler(CommandHandler("unban", filters=filters.Chat(settings.TELEGRAM_SUPPORT_CHAT_ID), callback=unban_callback))
    app.add_handler(CommandHandler("banlist", filters=filters.Chat(settings.TELEGRAM_SUPPORT_CHAT_ID), callback=banlist_callback))
    app.add_handler(CommandHandler("delete", filters=filters.Chat(settings.TELEGRAM_SUPPORT_CHAT_ID), callback=delete_callback))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE, await middleware(forward_to_chat)))
    app.add_handler(MessageHandler(filters.Chat(settings.TELEGRAM_SUPPORT_CHAT_ID) & filters.REPLY, await middleware(forward_to_user)))
    # app.add_error_handler(error_handler)

    schedule.every(settings.RATELIMIT_TIME_WINDOW_SEC).seconds.do(ratelimit_cleanup)
