import asyncio
from telegram import Chat, Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes

import settings

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
        user_id = None
        if update.message.reply_to_message.forward_from:
            user_id = update.message.reply_to_message.forward_from.id
        elif update.message.reply_to_message.text and settings.SUPPORT_SIDE__REPLY_TO_THIS_MESSAGE in update.message.reply_to_message.text or settings.SUPPORT_SIDE__USER_TRIED_FORWARDING_MESSAGE in update.message.reply_to_message.text:
            try:
                user_id = int(update.message.reply_to_message.text.split(' ')[0])
            except ValueError:
                user_id = None
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



def setup_dispatcher(app):
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE, forward_to_chat))
    app.add_handler(MessageHandler(filters.Chat(settings.TELEGRAM_SUPPORT_CHAT_ID) & filters.REPLY, forward_to_user))
