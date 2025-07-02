from datetime import datetime, timezone
from typing import List

from tortoise import Tortoise
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

import settings
from models import BoostLinkAccountUsageModel, AccountModel, BoostLinkModel, CampaignModel
from src.utils.logger import get_console_logger

logger = get_console_logger()


async def connect_db():
    logger.info("Connecting to database...")
    await Tortoise.init(
        db_url=settings.DB_URL,
        modules=settings.TORTOISE_MODULES
    )
    logger.info("Database connected.")


async def close_db():
    logger.info("Disconnecting database...")
    await Tortoise.close_connections()
    logger.info("Database disconnected.")


async def boost_link_ids_exist(boost_link_ids: List[int]):
    for boost_link_id in boost_link_ids:
        boost_link_obj = await BoostLinkModel.get_or_none(id=boost_link_id, is_deleted=False)
        if boost_link_obj is None:
            return False, f'{boost_link_id} 不存在'

    return True, f'检测成功'


async def get_running_tasks():
    return await CampaignModel.filter(status=1)


async def get_account_total_count():
    return await AccountModel.filter(is_deleted=False).count()


async def get_waiting_tasks():
    return await CampaignModel.filter(status=0).count()


async def get_completed_tasks():
    return await CampaignModel.filter(status=2).count()


async def statistics_account():
    account_queryset = AccountModel.filter(is_deleted=False)

    total_count = await account_queryset.count()

    invalid_count = await account_queryset.filter(status=1).count()

    now = datetime.now(timezone.utc)
    flood_count = await account_queryset.filter(flood_expire_at__gt=now, status=0).count()

    daily_boost_5count = await account_queryset.filter(daily_boost_count__gte=5, status=0).count()

    return total_count, invalid_count, flood_count, daily_boost_5count


async def get_campaigns_by_ids(campaign_ids: List[int]):
    campaign_objs = []
    for campaign_id in campaign_ids:
        campaign_obj = await CampaignModel.get_or_none(id=campaign_id)
        if campaign_obj is None:
            continue
        campaign_objs.append(campaign_obj)

    return campaign_objs


async def delete_accounts():
    active_campaign_objs_count = await CampaignModel.filter(Q(status=0) | Q(status=1)).count()

    if active_campaign_objs_count > 0:
        return False, '当前存在正在执行和等待执行的任务'

    await AccountModel.filter(is_deleted=False).update(is_deleted=True)

    return True, 'ok'


async def get_next_available_account_today(boost_link_id: int) -> AccountModel | None:
    async with in_transaction() as conn:
        now = datetime.now(timezone.utc)
        today = now.today()
        used_account_ids_today = [
            usage.account_id
            for usage in await BoostLinkAccountUsageModel.filter(boost_link_id=boost_link_id, boost_at=today)
        ]
        query = (
                Q(is_deleted=False)
                & Q(using_status=0)
                & Q(status=0)
                & (Q(flood_expire_at=None) | Q(flood_expire_at__lt=now))
                & Q(daily_boost_count__lt=5)
        )
        account_obj = (
            await AccountModel
            .filter(query)
            .order_by('last_used_at')
            .limit(1)
            .select_for_update()
            .first()
        )

        if account_obj is not None and account_obj.id not in used_account_ids_today:
            account_obj.using_status = 1
            account_obj.last_used_at = now
            await account_obj.save(using_db=conn, update_fields=['using_status', 'last_used_at'])
            return account_obj

        return None
