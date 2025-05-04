from telegram.ext import Application

from handlers import setup_dispatcher
from settings import TELEGRAM_TOKEN

application = Application.builder().token(TELEGRAM_TOKEN).build()
setup_dispatcher(application)
print("Running!")
application.run_polling()

