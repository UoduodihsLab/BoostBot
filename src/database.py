from datetime import datetime, timezone
from typing import List

from tortoise import Tortoise
from tortoise.expressions import Q

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


async def get_available_accounts(boost_link_id: int):
    now = datetime.now(tz=timezone.utc)
    today = now.today()
    used_account_ids_today = [
        account.id for account in await (
            BoostLinkAccountUsageModel
            .filter(boost_link_id=boost_link_id, boost_at__lt=today)
        )
    ]
    valid_accounts_count = await AccountModel.filter(
        status=0,
        flood_expire_at__lt=now,
        daily_boost_count__lt=5,
        is_deleted=False
    )

    available_accounts = []

    for account in valid_accounts_count:
        if account.id in used_account_ids_today:
            continue

        available_accounts.append(account)

    return available_accounts


async def boost_link_ids_exist(boost_link_ids: List[int]):
    for boost_link_id in boost_link_ids:
        boost_link_obj = await BoostLinkModel.get_or_none(id=boost_link_id, is_deleted=False)
        if boost_link_obj is None:
            return False, f'{boost_link_id} 不存在'

    return True


async def get_active_campaigns():
    query = Q(status=0) | Q(status=1)
    campaigns = await CampaignModel.filter(query)

    return campaigns
