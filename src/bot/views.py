from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.bot.navigation import push_navigation_stack


@push_navigation_stack
async def home_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = '欢迎使用助力机器人'

    keyboard = [
        [
            InlineKeyboardButton('创建助力任务', callback_data='boost_links_view'),
            InlineKeyboardButton('上传助力链接', callback_data='upload_boost_links')
        ],
        [
            InlineKeyboardButton('账号统计', callback_data='accounts_statistics_view'),
            InlineKeyboardButton('上传账号', callback_data='upload_accounts')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text=text, reply_markup=reply_markup)


@push_navigation_stack
async def boost_links_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass
