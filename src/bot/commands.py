from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.bot.views import home_view
from src.database import get_active_campaigns
from models import BoostLinkModel


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await home_view(update, context)


async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    campaigns = await get_active_campaigns()

    text = '暂无任务'
    for campaign in campaigns:
        boost_link_obj = await BoostLinkModel.get_or_none(id=campaign.boost_link_id)
        status_text = ''
        if campaign.status == 0:
            status_text = '等待执行'
        elif campaign.status == 1:
            status_text = '正在运行'
        text = (
            f'任务id: {campaign.id}\n'
            f'状态: {status_text}\n'
            f'- 链接编号: {boost_link_obj.param}\n'
            f'- 可用账号总数: {campaign.total_assigned}\n'
            f'- 成功次数: {campaign.success_count}\n'
            f'- 失败次数: {campaign.fail_count}\n'
            f'- 重复次数: {campaign.repeat_count}\n'
            f'------------------------------\n'
        )

    await context.bot.send_message(update.effective_chat.id, text=text)
