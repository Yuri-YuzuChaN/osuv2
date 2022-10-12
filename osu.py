import os, asyncio
from nonebot import NoneBot
from hoshino.service import sucmd
from hoshino.typing import CQEvent, CommandSession
from typing import Union, List
from asyncio.tasks import Task

from .src.sql import USER
from .src.file import MapDownload
from .src.api import token
from .src.mods import NEWMODS
from .src.error import ModsError, UserEnterError, UserNotBindError
from .src.draw import *
from . import sv, GAMEMODE

def InfoRecent(user: tuple, args: list) -> Union[str, list]:
    mode, isint = 0, False
    data = None
    if not args:
        if not user:
            raise UserNotBindError
        else:
            id, mode = user[0], user[2]
            isint = True
    elif len(args) == 1:
        if ':' in args[-1] or '：' in args[-1]:
            if not user:
                raise UserNotBindError
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

info_ali = ['info', 'Info', 'INFO']
recent_ali = ['recent', 're', 'RECENT', 'RE', 'Recent', 'Re']
pass_recent_ali = ['passrecent', 'pr', 'Pr', 'PR']
tbp_ali = ['tbp', 'Tbp', 'TBP', 'todaybp', 'Todaybp', 'TODAYBP']
score_ali = ['score', 'SCORE', 'Score']
bp_ali = ['bp', 'Bp', 'BP']
tr_ali = ['tr', 'Tr', 'TR', 'todayre', 'Todayre', 'TODAYRE', 'todayrecent', 'Todayrecent', 'TODAYRECENT']

@sv.on_prefix(info_ali)
@sv.on_prefix(recent_ali)
@sv.on_prefix(pass_recent_ali)
@sv.on_prefix(tbp_ali)
@sv.on_prefix(tr_ali)
async def osuinfo(bot: NoneBot, ev: CQEvent):
    try:
        qqid = ev.user_id
        cmd: str = ev.prefix.lower()
        args: str = ev.message.extract_plain_text().strip()
        for message in ev.message:
            if message.type == 'at':
                qqid = int(message.data['qq'])
        
        mode = 0
        pattern = re.compile(r'^([A-Za-z0-9\s]+)?\s?[:：]?([0-3]+)?$')
        match = pattern.search(args)
        if match.group(1):
            id = match.group(1).strip()
        else:
            user = USER.get_user_info(qqid)
            id = user[0]
            mode = user[2]
        if match.group(2):
            mode = int(match.group(2).strip())
        isint = str(id).isdigit()

        if cmd in info_ali:
            data = await draw_info(id, GAMEMODE[mode], isint)
        elif cmd in recent_ali:
            data = await draw_score('recent', id, GAMEMODE[mode], isint=isint)
        elif cmd in pass_recent_ali:
            data = await draw_score('passrecent', id, GAMEMODE[mode], isint=isint)
        elif cmd in tbp_ali:
            data = await best_pfm('tbp', id, GAMEMODE[mode], isint=isint)
        else:
            data = await best_pfm('tr', id, GAMEMODE[mode], isint=isint)
    except UserNotBindError as e:
        data = str(e)
    except Exception as e:
        sv.logger.error(traceback.format_exc())
        data = type(e)

    await bot.send(ev, data)

def Mods2list(args: str) -> List[str]:
    tempmods = ''
    mods = []
    for n, v in enumerate(args):
        if n % 2 == 1:
            if (m := tempmods + v.upper()) not in NEWMODS:
                raise ModsError(f'无法识别Mods -> [{m}]')
            mods.append(m)
        else:
            tempmods = v.upper()
    return mods

def ScoreBpInfo(user: tuple, args: List[str]) -> Tuple[Union[int, str], int, int, List[str], bool]:
    """`(osuid, mode, mapid/best, mods, isint)`"""
    mods = []
    isint = False
    if user:
        id: Union[int, str] = user[0]
        mode: int = user[2]
    else:
        id = ''
        mode = 0

    if len(args) == 1:
        if not args[0].isdigit():
            raise UserEnterError
        data = args[0]
        isint = True
    elif len(args) == 2:
        if (':' in args[1] or '：' in args[1]) and args[0].isdigit(): 
            if not user:
                raise UserNotBindError
            mode = int(args[1][1])
            data = args[0]
            isint = True
        elif '+' in args[1] and args[0].isdigit():
            if not user:
                raise UserNotBindError
            mods = Mods2list(args[1][1:])
            data = args[0]
            isint = True
        elif args[1].isdigit():
            id = args[0]
            data = args[1]
            isint = False
        else:
            raise UserEnterError
    elif len(args) == 3:
        if (':' in args[1] or '：' in args[1]) and '+' in args[2] and args[0].isdigit():
            if not user:
                raise UserNotBindError
            else:
                mods = Mods2list(args[2][1:])
                id, mode, data = user[0], int(args[1][1]), args[0]
                isint = True
        elif (':' in args[2] or '：' in args[2]) and args[1].isdigit():
            id, mode, data = args[0], int(args[2][1]), args[1]
        elif '+' in args[2] and args[1].isdigit():
            mods = Mods2list(args[2][1:])
            id, data = args[0], args[1]
        else:
            raise UserEnterError
    else:
        if (':' in args[-1] or '：' in args[-1]) and args[-2].isdigit():
            id, mode, data = ' '.join(args[:len(args)-2]), int(args[-1][1]), args[-2]
        elif '+' in args[-1] and args[-2].isdigit():
            mods = Mods2list(args[-1][1:])
            id, data = ' '.join(args[:len(args)-2]), args[-2]
        elif '+' in args[-1] and (':' in args[-2] or '：' in args[-2]) and args[-3].isdigit():
            mods = Mods2list(args[-1][1:])
            id, mode, data = ' '.join(args[:len(args)-3]), int(args[-2][1]), args[-3]
        elif args[-1].isdigit():
            id, data= ' '.join(args[:len(args)-1]), args[-1]
        else:
            raise UserEnterError
    info = (id, mode, int(data), mods, isint)

    return info

@sv.on_prefix(score_ali)
@sv.on_prefix(bp_ali)
async def osuscore(bot: NoneBot, ev: CQEvent):
    try:
        qqid = ev.user_id
        cmd: str = ev.prefix.lower()
        args: str = ev.message.extract_plain_text().strip()
        text: str = args.split()
        if not text:
            if cmd in score_ali:
                await bot.send(ev, '请输入正确的地图ID')
            else:
                await bot.send(ev, '请输入正确的bp')
            return
        for message in ev.message:
            if message.type == 'at':
                qqid = int(message.data['qq'])

        user = USER.get_user_info(qqid)
        pattern = re.compile(r'^([0-9]+):?([0-3])?\+([A-Za-z]+)')
        match = pattern.search(args)
        if match:
            id = user[0]
            udata = int(match.group(1))
            mode = match.group(2) if match.group(2) else 0
            mods = Mods2list(match.group(3))
            isint = True
        else:
            info = ScoreBpInfo(user, text)
            id, mode, udata, mods, isint = info

        if cmd in score_ali:
            data = await draw_score('score', id, GAMEMODE[mode], mapid=udata, mods=mods, isint=isint)
        if cmd in bp_ali:
            if udata <= 0 or udata > 100:
                await bot.send(ev, '只允许查询 1-100 的成绩')
                return
            data = await draw_score('bp', id, GAMEMODE[mode], best=udata, mods=mods, isint=isint)
    except UserNotBindError as e:
        data = str(e)
    except UserEnterError as e:
        data = str(e)
    except ModsError as e:
        data = e.value
    except Exception as e:
        sv.logger.error(traceback.format_exc())
        data = type(e)
    await bot.send(ev, data)

def limits(args: str) -> list:
    limit = args.split('-')
    if not limit[0].isdigit() or not limit[1].isdigit():
        raise UserEnterError
    min, max = int(limit[0]), int(limit[1])
    return [min, max]

@sv.on_prefix(['pfm', 'Pfm', 'PFM'])
async def osupfm(bot: NoneBot, ev: CQEvent):
    try:
        qqid = ev.user_id
        args: str = ev.message.extract_plain_text().strip().split()
        isint = False
        if not args:
            raise UserEnterError
        for message in ev.message:
            if message.type == 'at':
                qqid = int(message.data['qq'])
        
        user = USER.get_user_info(qqid)
        if len(args) == 1:
            if not user:
                raise UserNotBindError
            else:
                min, max = await limits(args[0])
                id, mode, mods = user[0], user[2], 0
                isint = True
        elif len(args) == 2:
            if (':' in args[1] or '：' in args[1]) and '-' in args[0]:
                if not user:
                    raise UserNotBindError
                else:
                    min, max = await limits(args[0])
                    id, mode, mods = user[0], int(args[1][1]), 0
                    isint = True
            elif '+' in args[1] and '-' in args[0]:
                if not user:
                    raise UserNotBindError
                else:
                    min, max = await limits(args[0])
                    id, mode, mods = user[0], user[2], Mods2list(args[1][1:])
                    isint = True
            elif '-' in args[0]:
                min, max = await limits(args[1])
                id, mode, mods = args[0], user[2], 0
            else:
                await bot.finish(ev, '请输入正确的参数')
        elif len(args) == 3:
            if (':' in args[1] or '：' in args[1]) and '+' in args[2] and '-' in args[0]:
                if not user:
                    raise UserNotBindError
                else:
                    min, max = await limits(args[0])
                    mods = Mods2list(args[2][1:])
                    id, mode = user[0], int(args[1][1])
                    isint = True
            elif '+' in args[2] and '-' in args[1]:
                min, max = await limits(args[1])
                mods = Mods2list(args[2][1:])
                id, mode = args[0], 0
            elif (':' in args[2] or '：' in args[2]) and '-' in args[1]:
                min, max = await limits(args[1])
                id, mode, mods = args[0], int(args[2][1]), 0
            else:
                await bot.finish(ev, '请输入正确的参数')
        else:
            if (':' in args[-1] or '：' in args[-1]) and '-' in args[-2]:
                min, max = await limits(args[-2])
                id, mode, mods = ' '.join(args[:len(args)-2]), int(args[-1][1]), 0
            elif '+' in args[-1] and '-' in args[-2]:
                min, max = await limits(args[-2])
                mods = Mods2list(args[-1][1:])
                id, mode = ' '.join(args[:len(args)-2]), 0
            elif '+' in args[-1] and (':' in args[-2] or '：' in args[-2]) and '-' in args[-3]:
                min, max = await limits(args[-3])
                mods = Mods2list(args[-1][1:])
                id, mode = ' '.join(args[:len(args)-3]), int(args[-2][1])
            elif '-' in args[-1]:
                min, max = await limits(args[-1])
                id, mode, mods = ' '.join(args[:len(args)-1]), 0, 0
            else:
                await bot.finish(ev, '请输入正确的参数')
        
        if min > 100 or max > 100:
            await bot.finish(ev, '只允许查询bp 1-100 的成绩')
        if min >= max:
            await bot.finish(ev, '请输入正确的bp范围')

        data = await best_pfm('pfm', id, GAMEMODE[mode], min, max, mods, isint)
    except UserNotBindError as e:
        data = str(e)
    except UserEnterError as e:
        data = str(e)
    except ModsError as e:
        data = e.value
    except Exception as e:
        sv.logger.error(traceback.format_exc())
        data = type(e)
    await bot.send(ev, data)

@sv.on_prefix(['map', 'Map', 'MAP'])
async def osumap(bot: NoneBot, ev: CQEvent):
    try:
        args: str = ev.message.extract_plain_text().strip()
        mods = []
        if not args:
            await bot.finish(ev, '请输入地图ID')
        elif not args[0].isdigit():
            await bot.finish(ev, '请输入正确的地图ID')
        if '+' in args[-1]:
            mods = Mods2list(args[-1][1:])
            del args[-1]
        info = await map_info(args[0], mods)
    except ModsError as e:
        info = e.value
    except Exception as e:
        sv.logger.error(traceback.format_exc())
        info = type(e)
    await bot.send(ev, info)

@sv.on_prefix(['bmap', 'Bmap', 'BMAP'])
async def osubmap(bot: NoneBot, ev: CQEvent):
    args: str = ev.message.extract_plain_text().strip().split()
    if not args:
        await bot.finish(ev, '请输入地图ID')
    op = False
    if len(args) == 1:
        if not args[0].isdigit():
            await bot.finish(ev, '请输入正确的地图ID')
        setid = args[0]
    elif args[0] == '-b':
        if not args[1].isdigit():
            await bot.finish(ev, '请输入正确的地图ID')
        op = True
        setid = args[1]
    else:
        await bot.finish(ev, '请输入正确的地图ID')
    info = await bmap_info(setid, op)
    await bot.send(ev, info)

@sv.on_prefix(['osudl', 'Osudl', 'OSUDL'])
async def osudl(bot: NoneBot, ev: CQEvent):
    gid = ev.group_id
    setid = ev.message.extract_plain_text().strip()
    if not setid or not setid.isdigit():
        await bot.finish('请输入正确的地图ID')
    file, name = await MapDownload(setid, True)
    await bot.upload_group_file(group_id=gid, file=file, name=name)
    os.remove(file)

@sv.on_prefix(['bind', 'Bind', 'BIND'])
async def osubind(bot: NoneBot, ev: CQEvent):
    qqid = ev.user_id
    id = ev.message.extract_plain_text().strip()
    if not id:
        await bot.finish(ev, '请输入您的 osuid', at_sender=True)
    try:
        if USER.get_user_info(qqid):
            await bot.finish(ev, '您已绑定，如需要解绑请输入 unbind', at_sender=True)
    except UserNotBindError:
        data = await bindinfo('bind', id, qqid)
    await bot.send(ev, data, at_sender=True)

@sv.on_prefix(['unbind', 'Unbind', 'UNBIND'])
async def osuunbind(bot: NoneBot, ev: CQEvent):
    qqid = ev.user_id
    user = USER.get_user_info(qqid)
    if user: 
        deluser = USER.delete_user(qqid)
        if deluser:
            await bot.send(ev, '解绑成功！', at_sender=True)
            USER.delete_user_info(user[0])
        else:
            await bot.send(ev, '数据库错误', at_sender=True)
    else:
        await bot.send(ev, '尚未绑定，无需解绑', at_sender=True)

@sv.on_prefix(['update', 'Update', 'UPDATE'])
async def osuupdate(bot: NoneBot, ev: CQEvent):
    try:
        qqid = ev.user_id
        args: str = ev.message.extract_plain_text().strip().split()
        USER.get_user_info(qqid)
        if not args:
            data = '请输入需要更新内容的参数'
        elif args[0] == 'mode':
            try:
                mode = int(args[1])
            except:
                await bot.finish('请输入更改的模式！')
            if mode >= 0 or mode < 4:
                result = USER.update_user_mode(qqid, mode)
                if result:
                    data = f'已将默认模式更改为 {GAMEMODENAME[mode]}'
                else:
                    data = '数据库错误'
            else:
                data = '请输入正确的模式 0-3'
        else:
            data = '参数错误，请输入正确的参数'
    except UserNotBindError as e:
        data = str(e)
    await bot.send(data)

@sv.on_prefix(['getbg', 'Getbg', 'GETBG'])
async def get_bg(bot: NoneBot, ev: CQEvent):
    id: str = ev.message.extract_plain_text().strip()
    if not id:
        msg = '请输入需要提取BG的地图ID'
    else:
        msg = await get_map_bg(id)
    await bot.send(ev, msg)

@sv.on_prefix(['osuhelp', 'Osuhelp', 'OSUHELP'])
async def osuhelp(bot: NoneBot, ev: CQEvent):
    await bot.send(ev, MessageSegment.image(os.path.join(PATH, 'help.png')))

@sucmd('更新OAuth')
async def update_oauth(session: CommandSession):
    await token.update_token()

@sv.scheduled_job('cron', hour='0', minute='0')
async def update_info():
    tasks: list[Task] = []
    result = USER.get_user_osuid()
    loop = asyncio.get_event_loop()
    for n, qqid in enumerate(result):
        task = loop.create_task(user(qqid[0], True))
        tasks.append(task)
        if n == 0:
            await asyncio.sleep(10)

    for _ in tasks:
        _.cancel()
        await asyncio.sleep(1)
    sv.logger.info(f'已更新{n + 1}位玩家数据')