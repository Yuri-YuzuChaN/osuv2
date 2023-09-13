from io import BytesIO
from typing import Union

import aiohttp

from .. import *


async def getImage(url: str) -> Union[BytesIO, Exception, Path]:
    try:
        if 'avatar-guest.png' in url:
            url = 'https://osu.ppy.sh/images/layout/avatar-guest.png'
        async with aiohttp.request('GET', url) as resp:
            if resp.status == 403:
                return WorkDir / 'mapbg.png'
            data = await resp.read()
        return BytesIO(data)
    except Exception as e:
        sv.logger.error(f'Image Failed: {e}')
        return e

