import re, os, asyncio
from hoshino.config import SUPERUSERS
from hoshino import Service, priv, logger
from hoshino.service import sucmd
from hoshino.typing import CQEvent, CommandSession
from nonebot import get_bot
from typing import Union
from asyncio.tasks import Task

from .sql import *
from .draw import *
from .file import MapDownload
from .api import token

sv = Service('osuv2', manage_priv=priv.ADMIN, enable_on_default=True)
helpimg = os.path.join(os.path.dirname(__file__), 'osufile', 'help.png')

GM = {0 : 'osu', 1 : 'taiko', 2 : 'fruits', 3 : 'mania'}
GMN = {0 : 'Std', 1 : 'Taiko', 2 : 'Ctb', 3 : 'Mania'}
USER = UserSQL()

def InfoRecent(user: tuple, args: list) -> Union[str, list]:
    mode, isint = 0, False
    data = None
    if not args:
        if not user:
            data = '该账号尚未绑定，请输入 bind 用户名 绑定账号'
        else:
            id, mode = user[0], user[2]
            isint = True
    elif len(args) == 1:
        if ':' in args[-1] or '：' in args[-1]:
            if not user:
                data = '该账号尚未绑定，请输入 bind 用户名 绑定账号'
            else:
                id = user[0]
                mode = int(args[-1][1])
                isint = True
        else:
            id = args[-1]
    else:
        if ':' in args[-1] or '：' in args[-1]:
            id = ' '.join(args[:len(args)-1])
            mode = int(args[-1][1])
        else:
            id = ' '.join(args[:len(args)])
    if not data:
        data: list[Union[str, int, bool]] = [id, mode, isint]

    return data

@sv.on_prefix(('info', 'INFO', 'Info'))
async def info(bot, ev:CQEvent):
    qqid = ev.user_id
    args: list[str] = ev.message.extract_plain_text().strip().split()
    while '' in args:
        args.remove('')
    if 'CQ:at' in str(ev.message):
        res = re.search(r'\[CQ:at,qq=(.*)\]', str(ev.message))
        qqid = int(res.group(1))
    user = USER.get_user(qqid)
    infodata = InfoRecent(user, args)
    if isinstance(infodata, str):
        data = infodata
    else:
        id, mode, isint = infodata
        data = await draw_info(id, GM[mode], isint)
    await bot.send(ev, data, at_sender=True)

@sv.on_prefix(('recent', 're', 'RECENT', 'RE', 'Recent', 'Re'))
async def recent(bot, ev:CQEvent):
    qqid = ev.user_id
    args: list[str] = ev.message.extract_plain_text().strip().split()
    while '' in args:
        args.remove('')
    if 'CQ:at' in str(ev.message):
        res = re.search(r'\[CQ:at,qq=(.*)\]', str(ev.message))
        qqid = int(res.group(1))
    user = USER.get_user(qqid)
    info = InfoRecent(user, args)
    if isinstance(info, str):
        data = info
    else:
        id, mode, isint = info
        data = await draw_score('recent', id, GM[mode], isint=isint)
    await bot.send(ev, data, at_sender=True)

def Msg2list(args: str) -> list:
    if '，' in args:
        liststr = '，'
    else:
        liststr = ','
    args = args.upper()
    return args[1:].split(liststr)

def ScoreBpInfo(user: tuple, args: List[str]) -> Union[list, str]:
    mode, mods, isint = 0, 0, False
    info = None
    if len(args) == 1:
        if not user:
            info = '该账号尚未绑定，请输入 bind 用户名 绑定账号'
        elif not args[0].isdigit():
            info = '请输入正确的地图ID'
        else:
            id, mode, data = user[0], user[2], args[0]
            isint = True
    elif len(args) == 2:
        if (':' in args[1] or '：' in args[1]) and args[0].isdigit(): 
            if not user:
                info = '该账号尚未绑定，请输入 bind 用户名 绑定账号'
            else:
                id, mode, data = user[0], int(args[1][1]), args[0]
                isint = True
        elif '+' in args[1] and args[0].isdigit():
            if not user:
                info = '该账号尚未绑定，请输入 bind 用户名 绑定账号'
            else:
                mods = Msg2list(args[1])
                id, mode, data = user[0], user[2], args[0]
                isint = True
        elif args[1].isdigit():
            id, data= args[0], args[1]
        else:
            info = '请输入正确的地图ID'
    elif len(args) == 3:
        if (':' in args[1] or '：' in args[1]) and '+' in args[2] and args[0].isdigit():
            if not user:
                info = '该账号尚未绑定，请输入 bind 用户名 绑定账号'
            else:
                mods = Msg2list(args[2])
                id, mode, data = user[0], int(args[1][1]), args[0]
                isint = True
        elif (':' in args[2] or '：' in args[2]) and args[1].isdigit():
            id, mode, data = args[0], int(args[2][1]), args[1]
        elif '+' in args[2] and args[1].isdigit():
            mods = Msg2list(args[2])
            id, data = args[0], args[1]
        else:
            info = '请输入正确的地图ID'
    else:
        if (':' in args[-1] or '：' in args[-1]) and args[-2].isdigit():
            id, mode, data = ' '.join(args[:len(args)-2]), int(args[-1][1]), args[-2]
        elif '+' in args[-1] and args[-2].isdigit():
            mods = Msg2list(args[-1])
            id, mode, data = ' '.join(args[:len(args)-2]), int(args[-1][1]), args[-2]
        elif '+' in args[-1] and (':' in args[-2] or '：' in args[-2]) and args[-3].isdigit():
            mods = Msg2list(args[-1])
            id, mode, data = ' '.join(args[:len(args)-3]), int(args[-2][1]), args[-3]
        elif args[-1].isdigit():
            id, data= ' '.join(args[:len(args)-1]), args[-1]
        else:
            info = '请输入正确的地图ID'
    if not info:
        info: list[Union[str, int, bool]] = [id, mode, int(data), mods, isint]

    return info

@sv.on_prefix(('score', 'SCORE', 'Score'))
async def score(bot, ev:CQEvent):
    qqid = ev.user_id
    args: list[str] = ev.message.extract_plain_text().strip().split()
    while '' in args:
        args.remove('')
    if not args:
        await bot.finish(ev, '请输入正确的地图ID', at_sender=True)
    if 'CQ:at' in str(ev.message):
        res = re.search(r'\[CQ:at,qq=(.*)\]', str(ev.message))
        qqid = int(res.group(1))
    user = USER.get_user(qqid)
    info = ScoreBpInfo(user, args)
    if isinstance(info, str):
        data = info
    else:
        id, mode, mapid, mods, isint = info
        data = await draw_score('score', id, GM[mode], mapid=mapid, mods=mods, isint=isint)
    await bot.send(ev, data, at_sender=True)

@sv.on_prefix(('bp', 'BP', 'Bp'))
async def bp(bot, ev:CQEvent):
    qqid = ev.user_id
    args: list[str] = ev.message.extract_plain_text().strip().split()
    while '' in args:
        args.remove('')
    if not args:
        await bot.finish(ev, '请输入正确的参数', at_sender=True)
    if 'CQ:at' in str(ev.message):
        res = re.search(r'\[CQ:at,qq=(.*)\]', str(ev.message))
        qqid = int(res.group(1))
    user = USER.get_user(qqid)
    info = ScoreBpInfo(user, args)
    if isinstance(info, str):
        data = info
    else:
        id, mode, best, mods, isint = info
        if best <= 0 or best > 50:
            await bot.finish(ev, '只允许查询bp 1-50 的成绩', at_sender=True)
        data = await draw_score('bp', id, GM[mode], best=best, mods=mods, isint=isint)
    await bot.send(ev, data, at_sender=True)

def limits(args: str) -> list:
    limit = args.split('-')
    min, max = int(limit[0]), int(limit[1])
    return [min, max]

@sv.on_prefix(('pfm', 'Pfm', 'PFM'))
async def pfm(bot, ev:CQEvent):
    qqid = ev.user_id
    isint = False
    args: list[str] = ev.message.extract_plain_text().strip().split()
    while '' in args:
        args.remove('')
    if not args:
        await bot.finish(ev, '请输入正确的参数', at_sender=True)
    elif 'CQ:at' in str(ev.message):
        result = re.search(r'\[CQ:at,qq=(.*)\]', str(ev.message))
        qqid = int(result.group(1))
    user = USER.get_user(qqid)
    if len(args) == 1:
        if not user:
            await bot.finish(ev, '该账号尚未绑定，请输入 bind 用户名 绑定账号', at_sender=True)
        else:
            min, max = limits(args[0])
            id, mode, mods = user[0], user[2], 0
            isint = True
    elif len(args) == 2:
        if (':' in args[1] or '：' in args[1]) and '-' in args[0]:
            if not user:
                await bot.finish(ev, '该账号尚未绑定，请输入 bind 用户名 绑定账号', at_sender=True)
            else:
                min, max = limits(args[0])
                id, mode, mods = user[0], int(args[1][1]), 0
                isint = True
        elif '+' in args[1] and '-' in args[0]:
            if not user:
                await bot.finish(ev, '该账号尚未绑定，请输入 bind 用户名 绑定账号', at_sender=True)
            else:
                min, max = limits(args[0])
                id, mode, mods = user[0], user[2], Msg2list(args[1])
                isint = True
        elif '-' in args[0]:
            min, max = limits(args[1])
            id, mode, mods = args[0], user[2], 0
        else:
            await bot.finish(ev, '请输入正确的参数', at_sender=True)
    elif len(args) == 3:
        if (':' in args[1] or '：' in args[1]) and '+' in args[2] and '-' in args[0]:
            if not user:
                await bot.finish(ev, '该账号尚未绑定，请输入 bind 用户名 绑定账号', at_sender=True)
            else:
                min, max = limits(args[0])
                mods = Msg2list(args[2])
                id, mode = user[0], int(args[1][1])
                isint = True
        elif '+' in args[2] and '-' in args[1]:
            min, max = limits(args[1])
            mods = Msg2list(args[2])
            id, mode = args[0], 0
        elif (':' in args[2] or '：' in args[2]) and '-' in args[1]:
            min, max = limits(args[1])
            id, mode, mods = args[0], int(args[2][1]), 0
        else:
            await bot.finish(ev, '请输入正确的参数', at_sender=True)
    else:
        if (':' in args[-1] or '：' in args[-1]) and '-' in args[-2]:
            min, max = limits(args[-2])
            id, mode, mods = ' '.join(args[:len(args)-2]), int(args[-1][1]), 0
        elif '+' in args[-1] and '-' in args[-2]:
            min, max = limits(args[-2])
            mods = Msg2list(args[-1])
            id, mode = ' '.join(args[:len(args)-2]), 0
        elif '+' in args[-1] and (':' in args[-2] or '：' in args[-2]) and '-' in args[-3]:
            min, max = limits(args[-3])
            mods = Msg2list(args[-1])
            id, mode = ' '.join(args[:len(args)-3]), int(args[-2][1])
        elif '-' in args[-1]:
            min, max = limits(args[-1])
            id, mode, mods = ' '.join(args[:len(args)-1]), 0, 0
        else:
            await bot.finish(ev, '请输入正确的参数', at_sender=True)
    
    if min > 100 or max > 100:
        await bot.finish(ev, '只允许查询bp 1-100 的成绩', at_sender=True)
    if min >= max:
        await bot.finish(ev, '请输入正确的bp范围', at_sender=True)

    data = await best_pfm('bp', id, GM[mode], min, max, mods, isint)
    await bot.send(ev, data, at_sender=True)

@sv.on_prefix(('tbp', 'Tbp', 'TBP'))
async def tbp(bot, ev:CQEvent):
    qqid = ev.user_id
    args: list[str] = ev.message.extract_plain_text().strip().split()
    while '' in args:
        args.remove('')
    if 'CQ:at' in str(ev.message):
        res = re.search(r'\[CQ:at,qq=(.*)\]', str(ev.message))
        qqid = int(res.group(1))
    user = USER.get_user(qqid)
    infodata = InfoRecent(user, args)
    if isinstance(infodata, str):
        data = infodata
    else:
        id, mode, isint = infodata
        data = await best_pfm('tbp', id, GM[mode], isint=isint)
    await bot.send(ev, data, at_sender=True)

@sv.on_prefix(('map', 'MAP', 'Map'))
async def map(bot, ev:CQEvent):
    mapid: list = ev.message.extract_plain_text().strip().split()
    mods = []
    while '' in mapid:
        mapid.remove('')
    if not mapid:
        await bot.finish(ev, '请输入地图ID', at_sender=True)
    elif not mapid[0].isdigit():
        await bot.finish(ev, '请输入正确的地图ID', at_sender=True)
    if '+' in mapid[-1]:
        mods = Msg2list(mapid[-1][1:])
        del mapid[-1]
    info = await map_info(mapid[0], mods)
    await bot.send(ev, info, at_sender=True)

@sv.on_prefix(('bmap', 'BMAP', 'Bmap'))
async def bmap(bot, ev:CQEvent):
    msg: list[str] = ev.message.extract_plain_text().strip().split()
    while '' in msg:
        msg.remove('')
    if not msg:
        await bot.finish(ev, '请输入地图ID', at_sender=True)
    op = False
    if len(msg) == 1:
        if not msg[0].isdigit():
            await bot.finish(ev, '请输入正确的地图ID', at_sender=True)
        setid = msg[0]
    elif msg[0] == '-b':
        if not msg[1].isdigit():
            await bot.finish(ev, '请输入正确的地图ID', at_sender=True)
        op = True
        setid = msg[1]
    else:
        await bot.finish(ev, '请输入正确的地图ID', at_sender=True)
    info = await bmap_info(setid, op)
    await bot.send(ev, info)

@sv.on_prefix(('osudl', 'Osudl', 'OSUDL'))
async def osudl(bot, ev:CQEvent):
    gid = ev.group_id
    setid: str = ev.message.extract_plain_text().strip()
    if not setid:
        return
    if not setid.isdigit():
        await bot.finish(ev, '请输入正确的地图ID', at_sender=True)
    file = await MapDownload(setid, True)
    await bot.upload_group_file(group_id=gid, file=file[0], name=file[1])
    os.remove(file[0])

@sv.on_prefix(('bind', 'BIND', 'Bind'))
async def bind(bot, ev:CQEvent):
    qqid = ev.user_id
    id = ev.message.extract_plain_text()
    if not id:
        await bot.finish(ev, '请输入您的 osuid', at_sender=True)
    if USER.get_user(qqid):
        await bot.finish(ev, '您已绑定，如需要解绑请输入unbind', at_sender=True)
    msg = await bindinfo('bind', id, qqid)
    await bot.send(ev, msg, at_sender=True)

@sv.on_prefix(('unbind', 'Unbind', 'UNBIND'))
async def unbind(bot, ev:CQEvent):
    qqid = ev.user_id
    user = USER.get_user(qqid)
    if user: 
        deluser = USER.delete_user(qqid)
        if deluser:
            await bot.send(ev, '解绑成功！', at_sender=True)
            USER.delete_info(user[0])
        else:
            await bot.send(ev, '数据库错误')
    else:
        await bot.send(ev, '尚未绑定，无需解绑', at_sender=True)

@sv.on_prefix(('update', 'UPDATE', 'Update'))
async def recent(bot, ev:CQEvent):
    qqid = ev.user_id
    args: list[str] = ev.message.extract_plain_text().strip().split()
    while '' in args:
        args.remove('')
    user = USER.get_user(qqid)
    if not user:
        msg = '该账号尚未绑定，请输入 bind 用户名 绑定账号'
    elif not args:
        msg = '请输入需要更新内容的参数'
    elif args[0] == 'mode':
        try:
            mode = int(args[1])
        except:
            await bot.finish(ev, '请输入更改的模式！', at_sender=True)
        if mode >= 0 or mode < 4:
            result = USER.update_mode(qqid, mode)
            if result:
                msg = f'已将默认模式更改为 {GMN[mode]}'
            else:
                msg = '数据库错误'
        else:
            msg = '请输入正确的模式 0-3'
    else:
        msg = '参数错误，请输入正确的参数'
    await bot.send(ev, msg, at_sender=True)

@sv.on_prefix(('getbg', 'Getbg', 'GETBG'))
async def get_bg(bot, ev:CQEvent):
    id = ev.message.extract_plain_text().strip()
    if not id:
        msg = '请输入需要提取BG的地图ID'
    else:
        msg = await get_map_bg(id)
    await bot.send(ev, msg, at_sender=True)

@sv.on_fullmatch('osuhelp')
async def recent(bot, ev:CQEvent):
    await bot.send(ev, MessageSegment.image(f'file:///{helpimg}'))

@sucmd('updateoauth', aliases=('更新OAuth'))
async def updateoauth(session: CommandSession):
    msg = await token.update_token()

@sv.scheduled_job('cron', hour='0')
async def update_info():
    tasks: list[Task] = []
    result = USER.get_user_osuid()
    loop = asyncio.get_event_loop()
    for n, qqid in enumerate(result):
        task = loop.create_task(user(qqid[0], True))
        tasks.append(task)
        await asyncio.sleep(1)
    await asyncio.sleep(10)

    for _ in tasks:
        _.cancel()
    logger.info(f'已更新{n+1}位玩家数据')
