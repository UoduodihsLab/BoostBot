from typing import List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from models import *
from src.bot.navigation import push_navigation_stack
from src.database import statistics_account, get_running_tasks, get_waiting_tasks, get_completed_tasks, \
    get_available_account_total_count_daily


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
        '查询执行中的任务: /running_tasks\n'
        '查询等待中的任务: /waiting_tasks\n'
        '查询已完成的任务: /completed_tasks\n'
        '清空所有账号: /clear_accounts'
    )

    await update.message.reply_text(text=text)


async def links_last_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data['links_pagination']['page'] -= 1
    page = context.chat_data['links_pagination']['page']
    size = context.chat_data['links_pagination']['size']
    queryset = BoostLinkModel.filter(is_deleted=False).order_by('id')
    total_count = await queryset.count()
    pages = total_count // size
    mod = total_count % size
    if mod != 0:
        pages += 1

    if pages < 1:
        text = '当前无频道链接, 请上传后再来'
        keyboard = [[InlineKeyboardButton('返回', callback_data='go_back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
        return

    text = '\n'.join(
        [
            f'{boost_link_obj.id} - {boost_link_obj.param}'
            for boost_link_obj in await queryset.offset(page * size).limit(size)
        ]
    )

    pagination_buttons = []
    if page > 0:
        pagination_buttons.append(InlineKeyboardButton('上一页', callback_data='links_last_page'))

    pagination_buttons.append(InlineKeyboardButton('下一页', callback_data='links_next_page'))

    op_buttons = [
        InlineKeyboardButton('创建助力任务', callback_data='on_create_boost_task'),
        InlineKeyboardButton('返回', callback_data='go_back')
    ]
    keyboard = [pagination_buttons, op_buttons]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)


async def links_next_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data['links_pagination']['page'] += 1
    page = context.chat_data['links_pagination']['page']
    size = context.chat_data['links_pagination']['size']
    queryset = BoostLinkModel.filter(is_deleted=False).order_by('id')
    total_count = await queryset.count()
    pages = total_count // size
    mod = total_count % size
    if mod != 0:
        pages += 1

    if pages < 1:
        text = '当前无频道链接, 请上传后再来'
        keyboard = [[InlineKeyboardButton('返回', callback_data='go_back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
        return

    text = '\n'.join(
        [
            f'{boost_link_obj.id} - {boost_link_obj.param}'
            for boost_link_obj in await queryset.offset(page * size).limit(size)
        ]
    )

    pagination_buttons = [
        InlineKeyboardButton('上一页', callback_data='links_last_page')
    ]
    if pages > page + 1:
        pagination_buttons.append(InlineKeyboardButton('下一页', callback_data='links_next_page'))

    op_buttons = [
        InlineKeyboardButton('创建助力任务', callback_data='on_create_boost_task'),
        InlineKeyboardButton('返回', callback_data='go_back')
    ]
    keyboard = [pagination_buttons, op_buttons]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)


@push_navigation_stack
async def boost_links_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data['links_pagination'] = {'page': 0, 'size': 10}
    page = context.chat_data['links_pagination']['page']
    size = context.chat_data['links_pagination']['size']
    queryset = BoostLinkModel.filter(is_deleted=False).order_by('id')
    total_count = await queryset.count()
    pages = total_count // size
    mod = total_count % size
    if mod != 0:
        pages += 1

    if pages < 1:
        text = '当前无频道链接, 请上传后再来'
        keyboard = [[InlineKeyboardButton('返回', callback_data='go_back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
        return

    text = '\n'.join(
        [
            f'{boost_link_obj.id} - {boost_link_obj.param}'
            for boost_link_obj in await queryset.offset(page * size).limit(size)
        ]
    )

    pagination_buttons = []
    if pages > page + 1:
        pagination_buttons.append(InlineKeyboardButton('下一页', callback_data='links_next_page'))

    keyboard = []
    if pagination_buttons:
        keyboard.append(pagination_buttons)

    keyboard.append([
        InlineKeyboardButton('创建助力任务', callback_data='on_create_boost_task'),
        InlineKeyboardButton('返回', callback_data='go_back')
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)


@push_navigation_stack
async def accounts_statistics_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # a: 账号总量
    # b: 当前可用
    # c: 今日限制
    # d: 助力5次
    # e: 总冻结量
    # f: 今日冻结
    a, b, c, d, e, f = await statistics_account()

    text = (f'账号总量: {a}\n'
            f'当前可用: {b}\n'
            f'今日限制: {c}\n'
            f'助力5次: {d}\n'
            f'总冻结量: {e}\n'
            f'今日冻结: {f}'
            )

    keyboard = [
        [
            InlineKeyboardButton('返回', callback_data='go_back')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)


async def running_tasks_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks = await get_running_tasks()

    text = ''
    for task in tasks:
        boost_link_obj = await BoostLinkModel.get_or_none(id=task.boost_link_id)
        account_total_count = await get_available_account_total_count_daily(boost_link_obj.id)
        text += (
            f'任务id: {task.id}\n'
            f'- 状态: 执行中\n'
            f'- 链接: {boost_link_obj.param}\n'
            f'- 当前可用账号总数: {account_total_count}\n'
            f'- 成功次数: {task.success_count}\n'
            f'- 失败次数: {task.fail_count}\n'
            f'- 重复次数: {task.repeat_count}\n'
            f'------------------------------\n'
        )

    if text == '':
        text = '暂无执行中的任务'

    await context.bot.send_message(update.effective_chat.id, text=text)


async def waiting_tasks_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks = await get_waiting_tasks()

    text = ''
    for task in tasks:
        boost_link_obj = await BoostLinkModel.get_or_none(id=task.boost_link_id)
        account_total_count = await get_available_account_total_count_daily(boost_link_obj.id)
        text += (
            f'任务id: {task.id}\n'
            f'- 状态: 等待中\n'
            f'- 链接: {boost_link_obj.param}\n'
            f'- 当前账号总数: {account_total_count}\n'
            f'- 成功次数: {task.success_count}\n'
            f'- 失败次数: {task.fail_count}\n'
            f'- 重复次数: {task.repeat_count}\n'
            f'------------------------------\n'
        )

    if text == '':
        text = '暂无等待中的任务'

    await context.bot.send_message(update.effective_chat.id, text=text)


async def completed_tasks_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks = await get_completed_tasks()

    text = ''
    for task in tasks:
        boost_link_obj = await BoostLinkModel.get_or_none(id=task.boost_link_id)
        text += (
            f'任务id: {task.id}\n'
            f'- 状态: 已完成\n'
            f'- 链接: {boost_link_obj.param}\n'
            f'- 成功次数: {task.success_count}\n'
            f'- 失败次数: {task.fail_count}\n'
            f'- 重复次数: {task.repeat_count}\n'
            f'------------------------------\n'
        )

    if text == '':
        text = '暂无已完成的任务'

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
