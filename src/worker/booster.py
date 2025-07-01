import asyncio

from telethon import TelegramClient
from telethon.errors import (
    SessionRevokedError,
    AuthKeyUnregisteredError,
    UserDeactivatedError,
    FloodWaitError
)

from src.status import BOOST_SUCCESS, BOOST_REPEATED, INVALID_ACCOUNT, FLOOD, BOOST_FAILED
from src.utils.logger import get_console_logger

logger = get_console_logger()


class Booster(TelegramClient):
    def __init__(self, session: str, api_id: int, api_hash: str):
        super().__init__(session, api_id, api_hash)

    async def boost(self, bot: str, command: str, param: str):
        boost_message = f'/{command} {param}'

        try:
            bot_entity = await self.get_entity(bot)
            async with self.conversation(bot_entity, timeout=30) as conv:
                await conv.send_message(boost_message)

                while True:
                    response = await conv.get_response(timeout=10)
                    message_text = response.text

                    logger.info(message_text)

                    if '助力成功' in message_text or '新人' in message_text:
                        return BOOST_SUCCESS, {'error': 'BOOST_SUCCESS', 'detail': {}}

                    if '已经助力过' in message_text:
                        return BOOST_REPEATED, {'error': 'BOOST_REPEATED', 'detail': {}}
        except SessionRevokedError as session_revoked_error:
            logger.error(session_revoked_error)
            return INVALID_ACCOUNT, {'error': 'SessionRevokedError', 'detail': {}}
        except AuthKeyUnregisteredError as auth_key_unregistered_error:
            logger.error(auth_key_unregistered_error)
            return INVALID_ACCOUNT, {'error': 'AuthKeyUnregisteredError', 'detail': {}}
        except UserDeactivatedError as user_deactivated_error:
            logger.error(user_deactivated_error)
            return INVALID_ACCOUNT, {'error': 'UserDeactivatedError', 'detail': {}}
        except FloodWaitError as flood_wait_error:
            logger.error(flood_wait_error)
            return FLOOD, {'error': 'FloodWaitError', 'detail': {'flood_seconds': flood_wait_error.seconds}}
        except asyncio.TimeoutError as timeout_error:
            logger.error(timeout_error)
            return BOOST_SUCCESS, {'error': 'asyncio.TimeoutError', 'detail': {}}
        except Exception as e:
            logger.error(e)
            if 'No user has' in str(e) or 'The user has been deleted' in str(e):
                return INVALID_ACCOUNT, {'error': 'INVALID_ACCOUNT', 'detail': {}}
        return BOOST_FAILED, {'error': 'BOOST_FAILED', 'detail': {}}
