from typing import List

from models import *
from src.utils.logger import get_console_logger

logger = get_console_logger()


async def create_campaign(boost_link_ids: List[int]):
    campaigns = []
    for boost_link_id in boost_link_ids:
        boost_link = await BoostLinkModel.get_or_none(id=boost_link_id, is_deleted=False)
        if boost_link is None:
            return False, {'message': f'助力链接 {boost_link_id} 不存在'}

        campaigns.append(CampaignModel(boost_link_id=boost_link_id))

    try:
        await CampaignModel.bulk_create(campaigns)
    except Exception as e:
        logger.error(e)
        return False, {'message': '助力任务创建失败'}

    return True, {'message': '助力任务创建成功'}
