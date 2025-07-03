from telegram import Update
from telegram.ext import ContextTypes

from src.bot.views import (
    home_view,
    running_tasks_view,
    waiting_tasks_view,
    completed_tasks_view,
    task_detail_view,
    help_view
)
from src.database import get_campaigns_by_ids, delete_accounts
from src.utils.logger import get_console_logger

logger = get_console_logger()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await home_view(update, context)


async def help_(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await help_view(update, context)


async def running_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await running_tasks_view(update, context)


async def waiting_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await waiting_tasks_view(update, context)


async def completed_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await completed_tasks_view(update, context)


async def query_task_by_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    if len(args) == 0:
        await context.bot.send_message(update.effective_chat.id, text='命令后需要带上任务id')
        return

    try:
        task_ids = list(map(int, args))
    except Exception as e:
        logger.error(e)
        await context.bot.send_message(update.effective_chat.id, text='你的输入包含无效的任务id, 请重新输入')
        return

    campaign_objs = await get_campaigns_by_ids(task_ids)

    if len(campaign_objs) == 0:
        await context.bot.send_message(update.effective_chat.id, '你输入的任务id没有找到对应的任务')
        return

    await task_detail_view(update, context, campaign_objs)


async def clear_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text='正在清空账号...')

    success, error_message = await delete_accounts()

    if not success:
        await update.message.reply_text(text=error_message)
        return

    await update.message.reply_text(text='账号清空成功')
