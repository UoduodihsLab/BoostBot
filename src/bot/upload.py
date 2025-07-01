from telegram import Update
from telegram.ext import ContextTypes

from models import AccountModel, BoostLinkModel
from src.bot.file import save_file, unzip_account_files, extract_boost_links
from src.bot.tools import parse_boost_link


async def handle_upload_account_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filename = update.message.document.file_name

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'正在保存 {filename} ...')
    zip_file_path = await save_file(update, context)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'正在解压 {filename} ...')
    account_list = await unzip_account_files(zip_file_path)
    for account in account_list:
        await AccountModel.update_or_create(
            phone=account[0],
            defaults={
                'session_path': account[1],
                'is_deleted': False
            }
        )

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'{filename} 上传成功')


async def handle_upload_boost_link_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filename = update.message.document.file_name

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'正在保存 {filename} ...')
    boost_links_file_path = await save_file(update, context)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'正在解析 {filename} ...')
    boost_links = await extract_boost_links(boost_links_file_path)

    boost_link_records = list(map(lambda link: parse_boost_link(link), boost_links))

    for boost_link_record in boost_link_records:
        await BoostLinkModel.update_or_create(
            link=boost_link_record[0],
            defaults={
                'bot': boost_link_record[1],
                'command': boost_link_record[2],
                'param': boost_link_record[3],
                'is_deleted': False
            }
        )

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'{filename} 解析成功')
