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
from src.bot.commands import (
    start,
    help_,
    running_tasks,
    waiting_tasks,
    completed_tasks,
    query_task_by_id,
    clear_accounts
)
from src.bot.conversations import BOOST_CONVERSATION
from src.bot.navigation import go_back
from src.bot.upload import handle_upload_boost_link_file, handle_upload_account_file
from src.bot.views import boost_links_view, accounts_statistics_view, links_next_page, links_last_page
from src.database import connect_db, close_db
from src.utils.logger import get_console_logger

logger = get_console_logger()


async def post_init(app: Application):
    commands = [
        BotCommand('start', '🚀启动机器人'),
        BotCommand('running_tasks', '👀 查看执行中任务'),
        BotCommand('waiting_tasks', '👀 查看等待中任务'),
        BotCommand('completed_tasks', '👀 查看已完成任务'),
        BotCommand('task_by_id', '🔍 查询任务'),
        BotCommand('clear_accounts', '🧹 清空账号'),
        BotCommand('help', '🔔 查看帮助')
    ]

    logger.info('setting commands...')
    await app.bot.set_my_commands(commands)
    logger.info('setting commands done.')


def run_bot():
    run_async(connect_db())
    app = (
        ApplicationBuilder()
        .token(settings.BOT_TOKEN)
        .post_init(post_init)
        .read_timeout(30)
        .write_timeout(30)
        .build()
    )

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_))
    app.add_handler(CommandHandler('running_tasks', running_tasks))
    app.add_handler(CommandHandler('waiting_tasks', waiting_tasks))
    app.add_handler(CommandHandler('completed_tasks', completed_tasks))
    app.add_handler(CommandHandler('task_by_id', query_task_by_id))
    app.add_handler(CommandHandler('clear_accounts', clear_accounts))

    app.add_handler(CallbackQueryHandler(boost_links_view, 'boost_links_view'))
    app.add_handler(CallbackQueryHandler(links_next_page, 'links_next_page'))
    app.add_handler(CallbackQueryHandler(links_last_page, 'links_last_page'))
    app.add_handler(CallbackQueryHandler(go_back, 'go_back'))
    app.add_handler(CallbackQueryHandler(start_boost, 'start_boost'))
    app.add_handler(CallbackQueryHandler(accounts_statistics_view, 'accounts_statistics_view'))

    app.add_handler(MessageHandler(filters.Document.ZIP, handle_upload_account_file))
    app.add_handler(MessageHandler(filters.Document.TXT, handle_upload_boost_link_file))

    app.add_handler(BOOST_CONVERSATION)

    try:
        app.run_webhook(
            listen=settings.WEBHOOK_LOCAL_LISTEN_IP,
            port=settings.WEBHOOK_LOCAL_LISTEN_PORT,
            url_path=settings.WEBHOOK_URL_PATH,
            webhook_url=settings.WEBHOOK_URL
        )
    except Exception as e:
        # logger.error(f'{traceback.print_exc()}')
        logger.error(e)
        run_async(close_db())


if __name__ == '__main__':
    run_bot()
