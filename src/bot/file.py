import os
import zipfile
from io import BytesIO

import aiofiles
from telegram import Update
from telegram.ext import ContextTypes

import settings
from src.utils.logger import get_console_logger

logger = get_console_logger()


async def save_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    file_id = update.message.document.file_id
    filename = update.message.document.file_name

    file = await context.bot.get_file(file_id)
    file_path = os.path.join(settings.BASE_DIR, 'uploads/tmp', filename)
    await file.download_to_drive(file_path)
    return file_path


async def unzip_account_files(zip_file_path: str):
    async with aiofiles.open(zip_file_path, 'rb') as zip_f:
        zip_data = await zip_f.read()

        with zipfile.ZipFile(BytesIO(zip_data)) as zip_ref:
            account_list = []
            sessions_dir = os.path.join(settings.BASE_DIR, 'uploads/sessions')
            for member in zip_ref.infolist():
                if not member.filename.endswith('.session'):
                    continue
                phone = os.path.split(member.filename)[0].split('/')[0]
                session_path = os.path.join(sessions_dir, member.filename)

                logger.info(f'{phone} - {session_path}')
                if not os.path.exists(session_path):
                    zip_ref.extract(member, sessions_dir)
                account_list.append((phone, session_path))

            return account_list


async def extract_boost_links(boost_links_file_path: str):
    boost_links = []
    async with aiofiles.open(boost_links_file_path, 'r', encoding='utf8') as f:
        async for line in f:
            boost_links.append(line.strip())

        return boost_links
