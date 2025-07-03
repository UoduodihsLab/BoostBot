import asyncio
from datetime import datetime, timezone, timedelta

import settings
from models import BoostLinkModel, CampaignModel, BoostLinkAccountUsageModel
from src.database import get_next_available_account_today
from src.status import *
from src.utils.logger import get_console_logger
from src.worker.booster import Booster

logger = get_console_logger()


async def exec_task(campaign_obj: CampaignModel):
    now = datetime.now(timezone.utc)
    campaign_obj.status = 1
    campaign_obj.requested_at = now
    await campaign_obj.save(update_fields=['status', 'requested_at'])

    boost_link_obj = await BoostLinkModel.get_or_none(id=campaign_obj.boost_link_id)
    account_obj = await get_next_available_account_today(boost_link_obj.id)
    while True:
        if account_obj is None:
            logger.info(f'{boost_link_obj.param} - 当前已无可用账号')
            break

        booster = Booster(account_obj.session_file, settings.API_ID, settings.API_HASH)
        logger.info(f'{account_obj.phone} - 正在连接 Telegram 服务器...')

        try:
            await booster.connect()
        except Exception as e:
            logger.error(f'{account_obj.phone}: {e}')

            account_obj.using_status = 0
            await account_obj.save(update_fields=['using_status'])

            account_obj = await get_next_available_account_today(boost_link_obj.id)
            continue

        if not booster.is_connected():
            logger.info(f'{account_obj.phone} - Telegram 服务器连接失败')
            campaign_obj.fail_count += 1
            await campaign_obj.save(update_fields=['fail_count'])

            account_obj.using_status = 0
            await account_obj.save(update_fields=['using_status'])

            account_obj = await get_next_available_account_today(boost_link_obj.id)
            continue

        logger.info(f'{account_obj.phone} - Telegram 服务器连接成功')

        if not await booster.is_user_authorized():
            logger.info(f'{account_obj.phone}: unauthorized')

            account_obj.status = 1
            account_obj.using_status = 0
            await account_obj.save(update_fields=['status', 'using_status'])

            campaign_obj.fail_count += 1
            await campaign_obj.save(update_fields=['fail_count'])

            account_obj = await get_next_available_account_today(boost_link_obj.id)
            continue

        status, message = await booster.boost(boost_link_obj.bot, boost_link_obj.command, boost_link_obj.param)

        # TODO: 判断客户端是否还在保持连接
        await booster.disconnect()

        if status == BOOST_SUCCESS:
            campaign_obj.success_count += 1
            await campaign_obj.save(update_fields=['success_count'])

            account_obj.daily_boost_count += 1
            await account_obj.save(update_fields=['daily_boost_count'])

            today = datetime.now(timezone.utc).today()
            boost_link_account_usage_obj = BoostLinkAccountUsageModel(
                boost_link_id=boost_link_obj.id,
                account_id=account_obj.id,
                boost_at=today
            )
            await boost_link_account_usage_obj.save()

        elif status == BOOST_FAILED:
            campaign_obj.fail_count += 1
            await campaign_obj.save(update_fields=['fail_count'])

        elif status == BOOST_REPEATED:
            campaign_obj.repeat_count += 1
            await campaign_obj.save(update_fields=['repeat_count'])

            today = datetime.now(timezone.utc).today()
            await BoostLinkAccountUsageModel.update_or_create(
                boost_link_id=boost_link_obj.id,
                account_id=account_obj.id,
                defaults={
                    'boost_at': today
                }
            )

        elif status == INVALID_ACCOUNT:
            account_obj.status = 1
            await account_obj.save(update_fields=['status'])

            campaign_obj.fail_count += 1
            await campaign_obj.save(update_fields=['fail_count'])

        elif status == FLOOD:
            now = datetime.now(timezone.utc)
            flood_seconds = message['detail']['flood_seconds']
            account_obj.flood_expire_at = now + timedelta(seconds=flood_seconds)
            await account_obj.save(update_fields=['flood_expire_at'])

            campaign_obj.fail_count += 1
            await campaign_obj.save(update_fields=['fail_count'])

        account_obj.using_status = 0
        await account_obj.save(update_fields=['using_status'])

        account_obj = await get_next_available_account_today(boost_link_obj.id)

        await asyncio.sleep(10)

    campaign_obj.status = 2
    await campaign_obj.save(update_fields=['status'])


async def schedule_tasks():
    campaign_objs = await CampaignModel.filter(status=0)

    tasks = []
    for campaign_obj in campaign_objs:
        t = asyncio.create_task(exec_task(campaign_obj))
        tasks.append(t)

    await asyncio.gather(*tasks)
