from functools import wraps

from telegram import Update
from telegram.ext import ContextTypes

from src.utils.logger import get_console_logger

logger = get_console_logger()


def push_navigation_stack(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
        if 'nav_stack' not in context.chat_data:
            context.chat_data['nav_stack'] = []

        context.chat_data['nav_stack'].append({'func': func, 'kwargs': kwargs})
        logger.info(f"Pushed to stack. New depth: {len(context.chat_data['nav_stack'])}")

        return await func(update, context, **kwargs)

    return wrapper
