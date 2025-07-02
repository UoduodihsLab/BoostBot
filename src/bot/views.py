from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from models import *
from src.bot.navigation import push_navigation_stack
from src.database import statistics_account


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

