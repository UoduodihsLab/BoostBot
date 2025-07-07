import asyncio
from datetime import datetime, timezone, timedelta

import settings
from models import BoostLinkModel, CampaignModel, BoostLinkAccountUsageModel
from src.database import get_next_available_account_today
from src.status import *
from src.utils.logger import get_console_logger
from src.worker.booster import Booster

logger = get_console_logger()

background_tasks = set()


async def exec_task(campaign_obj: CampaignModel):
    now = datetime.now(timezone.utc)
    campaign_obj.status = 1
    campaign_obj.requested_at = now
    await campaign_obj.save(update_fields=['status', 'requested_at'])

    boost_link_obj = await BoostLinkModel.get_or_none(id=campaign_obj.boost_link_id)

    while True:
        account_obj = await get_next_available_account_today(boost_link_obj.id)

        if account_obj is None:
            logger.info(f'{boost_link_obj.param} - 当前已无可用账号, 任务完成')
            break

        try:
            booster = Booster(account_obj.session_file, settings.API_ID, settings.API_HASH)

            logger.info(f'{account_obj.phone} - 正在连接 Telegram 服务器...')
            await booster.connect()
            logger.info(f'{account_obj.phone} - Telegram 服务器连接成功')

            status, message = await booster.boost(boost_link_obj.bot, boost_link_obj.command, boost_link_obj.param)

            if status == BOOST_SUCCESS:
                campaign_obj.success_count += 1
                await campaign_obj.save(update_fields=['success_count'])

                account_obj.daily_boost_count += 1
                await account_obj.save(update_fields=['daily_boost_count'])

                today = datetime.now(timezone.utc).date()
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

                today = datetime.now(timezone.utc).date()
                await BoostLinkAccountUsageModel.update_or_create(
                    boost_link_id=boost_link_obj.id,
                    account_id=account_obj.id,
                    defaults={
                        'boost_at': today
                    }
                )

            elif status == INVALID_ACCOUNT:
                campaign_obj.fail_count += 1
                await campaign_obj.save(update_fields=['fail_count'])

                account_obj.status = 1
                account_obj.frozen_at = datetime.now(timezone.utc).date()
                await account_obj.save(update_fields=['status', 'frozen_at'])

            elif status == FLOOD:
                campaign_obj.fail_count += 1
                await campaign_obj.save(update_fields=['fail_count'])

                now = datetime.now(timezone.utc)
                flood_seconds = message['detail']['flood_seconds']
                account_obj.flood_expire_at = now + timedelta(seconds=flood_seconds)
                await account_obj.save(update_fields=['flood_expire_at'])

        except Exception as e:
            logger.info(f'处理账号 {account_obj.phone} 时发生未知错误: {e}')

            campaign_obj.fail_count += 1
            await campaign_obj.save(update_fields=['fail_count'])
        finally:
            if 'booster' in locals() and booster.is_connected():
                await booster.disconnect()

            account_obj.using_status = 0
            await account_obj.save(update_fields=['using_status'])
            logger.info(f'{account_obj.phone} - 账号已经释放')

        await asyncio.sleep(10)

    campaign_obj.status = 2
    await campaign_obj.save(update_fields=['status'])


async def schedule_tasks():
    campaign_objs = await CampaignModel.filter(status=0)

    for campaign_obj in campaign_objs:
        t = asyncio.create_task(exec_task(campaign_obj))
        background_tasks.add(t)
        t.add_done_callback(background_tasks.discard)
