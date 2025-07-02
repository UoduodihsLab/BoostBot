import asyncio
from datetime import datetime, timezone, timedelta

import settings
from models import BoostLinkModel, CampaignModel, BoostLinkAccountUsageModel
from src.database import get_next_available_account_today
from src.status import *
from src.utils.logger import get_console_logger
from src.worker.booster import Booster

logger = get_console_logger()


async def exec_task(boost_link: BoostLinkModel, campaign_obj: CampaignModel):
    account_obj = await get_next_available_account_today(boost_link.id)
    while True:
        if account_obj is None:
            logger.info(f'{boost_link.param} - 当前已无可用账号')
            break

        booster = Booster(account_obj.session_file, settings.API_ID, settings.API_HASH)
        logger.info(f'{account_obj.phone} - 正在连接 Telegram 服务器...')

        try:
            await booster.connect()
        except Exception as e:
            logger.error(f'{account_obj.phone}: {e}')

            account_obj.using_status = 0
            await account_obj.save(update_fields=['using_status'])

            account_obj = await get_next_available_account_today(boost_link.id)
            continue

        if not booster.is_connected():
            logger.info(f'{account_obj.phone} - Telegram 服务器连接失败')
            campaign_obj.fail_count += 1
            await campaign_obj.save(update_fields=['fail_count'])

            account_obj.using_status = 0
            await account_obj.save(update_fields=['using_status'])

            account_obj = await get_next_available_account_today(boost_link.id)
            continue

        logger.info(f'{account_obj.phone} - Telegram 服务器连接成功')

        if not await booster.is_user_authorized():
            logger.info(f'{account_obj.phone}: unauthorized')

            account_obj.status = 1
            account_obj.using_status = 0
            await account_obj.save(update_fields=['status', 'using_status'])

            campaign_obj.fail_count += 1
            await campaign_obj.save(update_fields=['fail_count'])

            account_obj = await get_next_available_account_today(boost_link.id)
            continue

        status, message = await booster.boost(boost_link.bot, boost_link.command, boost_link.param)

        # TODO: 判断客户端是否还在保持连接
        await booster.disconnect()

        if status == BOOST_SUCCESS:
            campaign_obj.success_count += 1
            await campaign_obj.save(update_fields=['success_count'])

            account_obj.daily_boost_count += 1
            await account_obj.save(update_fields=['daily_boost_count'])

            today = datetime.now(timezone.utc).today()
            boost_link_account_usage_obj = BoostLinkAccountUsageModel(
                boost_link_id=boost_link.id,
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

        account_obj = await get_next_available_account_today(boost_link.id)

        await asyncio.sleep(10)


async def schedule_tasks():
    while True:
        campaign = await CampaignModel.filter(status=0).select_for_update().first()
        if campaign is None:
            break

        boost_link = await BoostLinkModel.get_or_none(id=campaign.boost_link_id, is_deleted=False)
        if boost_link is None:
            break

        try:
            campaign.status = 1
            campaign.requested_at = datetime.now(timezone.utc)
            await campaign.save(update_fields=['status', 'requested_at'])

            await exec_task(boost_link, campaign)

            campaign.status = 2
            await campaign.save(update_fields=['status'])
        except Exception as e:
            logger.error(f'{e}')
