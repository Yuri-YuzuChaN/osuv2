import asyncio
from asyncio import Task

from .. import *
from .Api import osuApi
from .DataBase import get_all_user_osuid, insert_user_daily_data
from .Model import User


async def update_daily_data() -> int:
    
    tasks: list[Task] = []
    result = get_all_user_osuid()
    loop = asyncio.get_event_loop()
    
    async def update(osuid: int, mode: str) -> User:
        data = await osuApi.user(osuid, mode)
        return User(**data)
    
    for mode in range(4):
        for user in result:
            task = loop.create_task(update(user.Osuid, mode=GameMode[mode]))
            tasks.append(task)
        
        done, pending = await asyncio.wait(tasks)
        userdata = [ _.result() for _ in done ]
        _in = insert_user_daily_data(mode, userdata)
        if _in:
            sv.logger.info(f'模式 {GameMode[mode]} 添加每日数据完成')
        else:
            sv.logger.error(f'模式 {GameMode[mode]} 添加每日数据错误')

        for _ in tasks:
            _.cancel()
    
    return len(result)