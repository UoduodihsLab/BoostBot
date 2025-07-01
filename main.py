from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from tortoise import run_async

import settings
from src.bot.navigation import go_back
from src.bot.views import *
from src.database import connect_db, close_db
from src.utils.logger import get_console_logger

logger = get_console_logger()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await home_view(update, context)


if __name__ == '__main__':
    bot_token = settings.BOT_TOKEN
    web_hook_url = f'https://boosterbot.uoduodihs.com/{bot_token}'

    run_async(connect_db())

    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler('start', start))

    app.add_handler(CallbackQueryHandler(boost_links_view, 'boost_links_view'))
    app.add_handler(CallbackQueryHandler(go_back, 'go_back'))

    try:
        app.run_webhook(
            listen='127.0.0.1',
            port=8443,
            url_path=bot_token,
            webhook_url=web_hook_url
        )
    except Exception as e:
        logger.error(e)
        run_async(close_db())
