from telegram.ext import Application

from handlers import setup_dispatcher
from settings import TELEGRAM_TOKEN
import asyncio

application = Application.builder().token(TELEGRAM_TOKEN).build()
asyncio.new_event_loop().run_until_complete(setup_dispatcher(application))
print("Running!")
application.run_polling()

