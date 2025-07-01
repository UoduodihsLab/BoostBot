from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters

from src.database import boost_link_ids_exist
from src.utils.logger import get_console_logger

logger = get_console_logger()

INPUTTING_BOOST_LINK_NOS = 0


async def on_create_boost_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = '请输入助力链接编号, 多个编号之间用一个空格隔开'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    return INPUTTING_BOOST_LINK_NOS


async def handle_input_boost_link_ids(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text

    try:
        boost_link_ids = list(map(int, ' '.split(message_text)))
    except Exception as e:
        logger.error(e)
        await context.bot.send_message(chat_id=update.effective_chat.id, text='链接编号输入有误， 请重新输入')
        return INPUTTING_BOOST_LINK_NOS

    is_exist, error_message = await boost_link_ids_exist(boost_link_ids)

    if not is_exist:
        text = (
            f'提示: {error_message}\n'
            f'请重新输入'
        )
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

        return INPUTTING_BOOST_LINK_NOS

    text = (
        f'你输入的助力链接编号是[{message_text}]\n'
        f'任务启动后，系统会按照顺序对你选择的链接执行助力任务,直到账号用尽'
    )

    context.chat_data['boost_link_ids'] = boost_link_ids

    keyboard = [
        [
            InlineKeyboardButton('开始助力', callback_data='start_boost'),
            InlineKeyboardButton('取消', callback_data='go_back')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(update.effective_chat.id, text=text, reply_markup=reply_markup)

    return ConversationHandler.END


BOOST_CONVERSATION = ConversationHandler(
    entry_points=[CallbackQueryHandler(on_create_boost_task, 'on_create_boost_task')],
    states={
        INPUTTING_BOOST_LINK_NOS: [
            MessageHandler(filters.TEXT, handle_input_boost_link_ids)
        ]
    },
    fallbacks=[]
)
