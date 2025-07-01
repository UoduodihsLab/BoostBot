import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from src.scheduler.core import schedule_tasks
from src.task.core import create_campaign


def task_done_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async def wrapper(task: asyncio.Task):

        if task.cancelled():
            await context.bot.send_message(chat_id=update.effective_chat.id, text='任务失败')
            return

        if task.exception():
            await context.bot.send_message(chat_id=update.effective_chat.id, text='任务执行异常')
            return

        context.chat_data['background_tasks'].discard(task)

        result = task.result()
        text = f'你有助力任务已完成, 请及时查看运行结果 {result}'
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    return wrapper


async def start_boost(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text='正在创建助力任务...')
    boost_link_ids = context.chat_data['boost_link_ids']
    success, error_message = await create_campaign(boost_link_ids)

    if not success:
        await context.bot.send_message(update.effective_chat.id, error_message)
        return

    await context.bot.send_message(chat_id=update.effective_chat.id, text='正在启动助力任务...')

    if 'background_tasks' not in context.chat_data:
        context.chat_data['background_tasks'] = set()

    task = asyncio.create_task(schedule_tasks())

    context.chat_data['background_tasks'].add(task)
    task.add_done_callback(task_done_cb(update, context))

    text = '助力任务已成功启动, 你可以输入命令 /running_tasks 查看任务实时进度'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
