from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.bot.navigation import push_navigation_stack


@push_navigation_stack
async def home_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = '欢迎使用助力机器人'

    keyboard = [
        [
            InlineKeyboardButton('助力链接列表', callback_data='boost_links_view'),
            InlineKeyboardButton('上传助力链接', callback_data='upload_boost_links')
        ],
        [
            InlineKeyboardButton('账号统计', callback_data='accounts_statistics_view'),
            InlineKeyboardButton('上传账号', callback_data='upload_accounts')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text, reply_markup=reply_markup)
