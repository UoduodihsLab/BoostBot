from typing import List

from tortoise.expressions import Q

from models import *
from src.database import get_available_accounts
from src.utils.logger import get_console_logger

logger = get_console_logger()


async def create_campaign(boost_link_ids: List[int]):
    campaign_objs_count = await CampaignModel.filter(Q(status=0) | Q(status=1)).count()
    if campaign_objs_count > 0:
        return False, {'message': '当前有任务正在进行, 请等待任务运行完毕后再创建任务'}
    campaigns = []
    for boost_link_id in boost_link_ids:
        boost_link = await BoostLinkModel.get_or_none(id=boost_link_id, is_deleted=False)
        if boost_link is None:
            return False, {'message': f'助力链接 {boost_link_id} 不存在'}

        campaign = await CampaignModel.get_or_none(boost_link_id=boost_link_id, status=1)
        if campaign is not None:
            # return False, {'message': '此链接已存在进行中的任务, 请勿重复创建'}
            continue

        valid_accounts = await get_available_accounts(boost_link_id)

        campaigns.append(CampaignModel(boost_link_id=boost_link_id, total_assigned=len(valid_accounts)))

    try:
        await CampaignModel.bulk_create(campaigns)
    except Exception as e:
        logger.error(e)
        return False, {'message': '助力任务创建失败'}

    return True, {'message': '助力任务创建成功'}
