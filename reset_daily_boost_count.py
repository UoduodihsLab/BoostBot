import asyncio
from datetime import datetime, timezone, timedelta

from tortoise.expressions import Q

from models import AccountModel
from src.database import connect_db, close_db
from src.utils.logger import get_console_logger

logger = get_console_logger()


async def reset():
    try:
        await connect_db()

        query = Q(is_deleted=False) & Q(using_status=0) & Q(status=0) & Q(daily_boost_count__gte=5)
        account_objs = await AccountModel.filter(query)

        now = datetime.now(timezone.utc)

        for account_obj in account_objs:
            reset_at = account_obj.last_used_at + timedelta(hours=24)

            if reset_at <= now:
                account_obj.daily_boost_count = 0
                await account_obj.save(update_fields=["daily_boost_count"])
                logger.info(f'{account_obj.phone} - 助力次数重置成功')
    except Exception as e:
        logger.error(e)
    finally:
        await close_db()


if __name__ == '__main__':
    asyncio.run(reset())
