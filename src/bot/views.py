from typing import List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from models import *
from src.bot.navigation import push_navigation_stack
from src.database import statistics_account, get_active_campaigns


@push_navigation_stack
async def home_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = '欢迎使用助力机器人'

    keyboard = [
        [
            InlineKeyboardButton('助力链接列表', callback_data='boost_links_view'),
            InlineKeyboardButton('账号统计', callback_data='accounts_statistics_view'),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text=text, reply_markup=reply_markup)


@push_navigation_stack
async def help_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        '助力任务创建输入频道编号示例: 1 2 3\n'
        '根据任务id查询示例: /task_by_id 1 2 3\n'
        '查询当前活动的任务: /list_tasks'
    )

    await update.message.reply_text(text=text)


@push_navigation_stack
async def boost_links_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = '当前无频道链接, 请上传后再来'
    keyboard = [
        [
            InlineKeyboardButton('返回', callback_data='go_back')
        ]
    ]
    boost_links = [
        f'{boost_link_obj.id} - {boost_link_obj.param}'
        for boost_link_obj in await BoostLinkModel.filter(is_deleted=False)
    ]

    if boost_links:
        text = '\n'.join(boost_links)
        keyboard = [
            [
                InlineKeyboardButton('创建助力任务', callback_data='on_create_boost_task'),
                InlineKeyboardButton('返回', callback_data='go_back')
            ]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)


@push_navigation_stack
async def accounts_statistics_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_count, invalid_count, flood_count, daily_boost_5count = await statistics_account()

    text = (f'账号总量: {total_count}\n'
            f'冻结总量: {invalid_count}\n'
            f'限制总量: {flood_count}\n'
            f'今日限额: {daily_boost_5count}'
            )

    keyboard = [
        [
            InlineKeyboardButton('返回', callback_data='go_back')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)


async def task_list_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    campaigns = await get_active_campaigns()

    text = ''
    for campaign in campaigns:
        boost_link_obj = await BoostLinkModel.get_or_none(id=campaign.boost_link_id)
        status_text = ''
        if campaign.status == 0:
            status_text = '等待执行'
        elif campaign.status == 1:
            status_text = '正在运行'
        else:
            status_text = '执行完毕'
        text += (
            f'任务id: {campaign.id}\n'
            f'状态: {status_text}\n'
            f'- 链接: {boost_link_obj.param}\n'
            f'- 可用账号总数: {campaign.total_assigned}\n'
            f'- 成功次数: {campaign.success_count}\n'
            f'- 失败次数: {campaign.fail_count}\n'
            f'- 重复次数: {campaign.repeat_count}\n'
            f'------------------------------\n'
        )

    if text == '':
        text = '暂无任务'

    await context.bot.send_message(update.effective_chat.id, text=text)


async def task_detail_view(update: Update, context: ContextTypes.DEFAULT_TYPE, tasks: List[CampaignModel]):
    text = ''
    for task in tasks:
        boost_link_obj = await BoostLinkModel.get_or_none(id=task.boost_link_id)
        status_text = ''
        if task.status == 0:
            status_text = '等待执行'
        elif task.status == 1:
            status_text = '正在运行'
        else:
            status_text = '执行完毕'
        text += (
            f'任务id: {task.id}\n'
            f'状态: {status_text}\n'
            f'- 链接: {boost_link_obj.param}\n'
            f'- 可用账号总数: {task.total_assigned}\n'
            f'- 成功次数: {task.success_count}\n'
            f'- 失败次数: {task.fail_count}\n'
            f'- 重复次数: {task.repeat_count}\n'
            f'------------------------------\n'
        )

    if text == '':
        text = '未查询到任务'

    await context.bot.send_message(update.effective_chat.id, text=text)
