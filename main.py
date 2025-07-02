import asyncio

from telegram import BotCommand
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from tortoise import run_async

import settings
from src.bot.boost_entry import start_boost
from src.bot.commands import start, list_tasks
from src.bot.conversations import BOOST_CONVERSATION
from src.bot.navigation import go_back
from src.bot.upload import handle_upload_boost_link_file, handle_upload_account_file
from src.bot.views import boost_links_view, accounts_statistics_view
from src.database import connect_db, close_db
from src.utils.logger import get_console_logger

logger = get_console_logger()


async def post_init(app: Application):
    commands = [
        BotCommand('start', '🚀启动机器人'),
        BotCommand('list_tasks', '📒 查看任务执行状态'),
    ]

    logger.info('setting commands...')
    await app.bot.set_my_commands(commands)
    logger.info('setting commands done.')


def run_bot():
    bot_token = settings.BOT_TOKEN
    web_hook_url = f'https://boosterbot.uoduodihs.com/{bot_token}'

    run_async(connect_db())
    app = (
        ApplicationBuilder()
        .token(bot_token)
        .post_init(post_init)
        .read_timeout(30)
        .write_timeout(30)
        .build()
    )

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('list_tasks', list_tasks))

    app.add_handler(CallbackQueryHandler(boost_links_view, 'boost_links_view'))
    app.add_handler(CallbackQueryHandler(go_back, 'go_back'))
    app.add_handler(CallbackQueryHandler(start_boost, 'start_boost'))
    app.add_handler(CallbackQueryHandler(accounts_statistics_view, 'accounts_statistics_view'))

    app.add_handler(MessageHandler(filters.Document.ZIP, handle_upload_account_file))
    app.add_handler(MessageHandler(filters.Document.TXT, handle_upload_boost_link_file))

    app.add_handler(BOOST_CONVERSATION)

    try:
        app.run_webhook(
            listen='127.0.0.1',
            port=8443,
            url_path=bot_token,
            webhook_url=web_hook_url
        )
    except Exception as e:
        # logger.error(f'{traceback.print_exc()}')
        logger.error(e)
        run_async(close_db())


if __name__ == '__main__':
    run_bot()
