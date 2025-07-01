import logging

from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

from src.bot.views import *

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logging.getLogger('httpx').setLevel(logging.WARNING)

logger = logging.getLogger('root')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await home_view(update, context)


if __name__ == '__main__':
    bot_token = '7206853820:AAGDpvJskONRyU2JNjHYuDUhdTrNvDxKa1Q'
    web_hook_url = f'https://boosterbot.uoduodihs.com/{bot_token}'

    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler('start', start))

    app.add_handler(CallbackQueryHandler(boost_links_view, 'boost_links_view'))

    app.run_webhook(
        listen='127.0.0.1',
        port=8443,
        url_path=bot_token,
        webhook_url=web_hook_url
    )
