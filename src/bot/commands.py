from telegram import Update
from telegram.ext import ContextTypes

from src.bot.views import home_view
from src.database import get_active_campaigns


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await home_view(update, context)


async def show_tasks(update: Update, context: ContextTypes):
    campaigns = await get_active_campaigns()

    text = ''
    for campaign in campaigns:
        text += f'{campaign.title}'


