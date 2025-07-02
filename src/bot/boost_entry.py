import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from src.scheduler.core import schedule_tasks
from src.task.core import create_campaign


async def start_boost(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text='正在创建助力任务...')

    boost_link_ids = context.chat_data['boost_link_ids']
    success, error_message = await create_campaign(boost_link_ids)
    if not success:
        await context.bot.send_message(update.effective_chat.id, error_message)
        return

    await context.bot.send_message(chat_id=update.effective_chat.id, text='正在启动助力任务...')

    task = asyncio.create_task(schedule_tasks())

    text = '助力任务已成功启动, 你可以输入命令 /list_tasks 查看活动中的任务实时进度'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
