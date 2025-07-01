from datetime import datetime, timezone

from tortoise import Tortoise

import settings
from models import BoostLinkAccountUsageModel, AccountModel
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
