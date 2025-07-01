from typing import Tuple
from urllib.parse import urlparse, parse_qs


def parse_boost_link(boost_link: str) -> Tuple[str, str, str, str]:
    parsed_url = urlparse(boost_link)
    path = parsed_url.path
    query_params = parse_qs(parsed_url.query)

    bot = path.split('/')[-1]
    command = ''
    param = ''

    for key, value in query_params.items():
        command = key
        param = value[0]
        break

    return boost_link, bot, command, param
