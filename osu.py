import re
import traceback
from typing import List

from hoshino.typing import CQEvent
from nonebot import NoneBot

from . import *
from .src import update_daily_data
from .src.DataBase import delete_user, get_user_data, insert_user, update_user_mode
from .src.Error import *
from .src.Picture import *

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
async def _(bot: NoneBot, ev: CQEvent):
    try:
        qqid = ev.user_id
        cmd: str = ev.prefix.lower()
        text: str = ev.message.extract_plain_text().strip()
        for message in ev.message:
            if message.type == 'at':
                qqid = int(message.data['qq'])
        
        mode = 0
        pattern = re.compile(r'^([A-Za-z0-9\s_-]+)?\s?[:：]?([0-3]+)?$')
        match = pattern.search(text)
        if match.group(1):
            user_id = match.group(1).strip()
        else:
            user = get_user_data(qqid)
            user_id = user.Osuid
            mode = user.Osumode
        if match.group(2):
            mode = int(match.group(2).strip())

        if cmd in info_ali:
            data = await draw_info(user_id, GameMode[mode])
        elif cmd in recent_ali:
            data = await draw_score('recent', user_id, GameMode[mode])
        elif cmd in pass_recent_ali:
            data = await draw_score('passrecent', user_id, GameMode[mode])
        elif cmd in tbp_ali:
            data = await best_pfm('tbp', user_id, GameMode[mode])
        else:
            data = await best_pfm('tr', user_id, GameMode[mode])
    except UserNotBindError as e:
        data = str(e)
    except Exception as e:
        sv.logger.error(traceback.format_exc())
        data = type(e)

    await bot.send(ev, data)


def mods2list(args: str) -> List[str]:
    tempmods = ''
    mods = []
    for n, v in enumerate(args):
        if n % 2 == 1:
            if (m := tempmods + v.upper()) not in NewMod:
                raise ModsError(f'无法识别Mods -> [{m}]')
            mods.append(m)
        else:
            tempmods = v.upper()
    return mods


@sv.on_prefix(score_ali)
@sv.on_prefix(bp_ali)
async def _(bot: NoneBot, ev: CQEvent):
    try:
        qqid = ev.user_id
        cmd: str = ev.prefix.lower()
        text = ev.message.extract_plain_text().strip().split()
        if not text:
            if cmd is score_ali:
                await bot.send(ev, '请输入正确的地图ID')
            else:
                await bot.send(ev, '请输入正确的bp')
            return
        for message in ev.message:
            if message.type == 'at':
                qqid = int(message.data['qq'])

        mode = 0
        mods = None
        pattern = re.compile(
            r'^([A-Za-z0-9\s_-]+)?\s([0-9]+)\s?[:：]?([0-9])?\s?\+?([A-Za-z]+)?')
        match = pattern.search(ev.message.extract_plain_text().strip())
        if match:
            if _u := match.group(1):
                user_id = _u
            else:
                user = get_user_data(qqid)
                user_id = user.Osuid

            map_best = int(match.group(2))
            if _m := match.group(3):
                mode = int(_m)
            if _ms := match.group(4):
                mods = mods2list(_ms)
        elif match2 := pattern.search(' ' + ev.message.extract_plain_text()):
            user_id = get_user_data(qqid).Osuid
            map_best = int(match2.group(2))

            if _m := match2.group(3):
                mode = int(_m)
            if _ms := match2.group(4):
                mods = mods2list(_ms)
        else:
            raise UserEnterError

        if cmd is score_ali:
            data = await draw_score('score', user_id, GameMode[mode], mapid=map_best, mods=mods)
        if cmd is bp_ali:
            if map_best <= 0 or map_best > 100:
                await bot.send(ev, '只允许查询 1-100 的成绩')
                return
            data = await draw_score('bp', user_id, GameMode[mode], best=map_best, mods=mods)
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


@sv.on_prefix(['pfm', 'Pfm', 'PFM'])
async def _(bot: NoneBot, ev: CQEvent):
    try:
        qqid = ev.user_id
        args = ev.message.extract_plain_text().strip()
        if not args:
            await bot.finish(ev, '请输入正确的参数')
        for message in args:
            if message.type == 'at':
                qqid = int(message.data['qq'])

        pattern = re.compile(
            r'^([A-Za-z0-9]+)?\s?([0-9]+)-([0-9]+)\s?([:：][0-9])?\s?(\+[A-Za-z]+)?')
        match = pattern.search(ev.message.extract_plain_text())

        user_id = None
        mode = 0
        mods = None

        min = match.group(2)
        max = match.group(3)
        if not min and not max:
            await bot.finish(ev, '请输入正确的bp范围')
        else:
            min = int(min)
            max = int(max)
        if min > 100 or max > 100:
            await bot.finish(ev, '只允许查询bp 1-100 的成绩')
        if min >= max:
            await bot.finish(ev, '请输入正确的bp范围')

        if _u := match.group(1):
            user_id = _u
            mode = 0
        else:
            user = get_user_data(qqid)
            user_id = user.Osuid
            mode = user.Osumode
        if _m := match.group(4):
            mode = int(_m[1:])
            if mode < 0 and mode > 3:
                await bot.finish(ev, '请输入正确的模式')
        if _ms := match.group(5):
            mods = mods2list(_ms)

        data = await best_pfm('pfm', user_id, GameMode[mode], min, max, mods)
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
        mapid: str = ev.message.extract_plain_text().strip()
        mods = []
        if not mapid:
            await bot.finish(ev, '请输入地图ID')
        elif not mapid[0].isdigit():
            await bot.finish(ev, '请输入正确的地图ID')
        if '+' in mapid[-1]:
            mods = mods2list(mapid[-1][1:])
            del mapid[-1]
        data = await draw_map(mapid[0], mods)
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
    info = await draw_beatmap(setid, op)
    await bot.send(ev, info)


@sv.on_prefix(['bind', 'Bind', 'BIND'])
async def osubind(bot: NoneBot, ev: CQEvent):
    qqid = ev.user_id
    osuid = ev.message.extract_plain_text().strip()
    if not osuid:
        await bot.finish(ev, '请输入您的 osuid', at_sender=True)
    if get_user_data(qqid):
        msg = '您已绑定，如需要解绑请输入 !unbind'
    else:
        data = await osuApi.user(osuid)
        if data:
            user = User(**data)
            _in = insert_user(qqid, user)
            if _in:
                msg = f'用户 {user.username} 已成功绑定QQ {qqid}'
            else:
                msg = '数据库错误'
        else:
            msg = '未找到玩家'
    await bot.send(ev, msg, at_sender=True)


@sv.on_prefix(['unbind', 'Unbind', 'UNBIND'])
async def osuunbind(bot: NoneBot, ev: CQEvent):
    try:
        qqid = ev.user_id
        get_user_data(qqid)
        deluser = delete_user(qqid)
        if deluser:
            data = '解绑成功'
        else:
            data = '数据库错误'
    except UserNotBindError:
        data = '玩家尚未绑定，无需解绑'
    await bot.send(ev, data, at_sender=True)


@sv.on_prefix(['update', 'Update', 'UPDATE'])
async def osuupdate(bot: NoneBot, ev: CQEvent):
    try:
        qqid = ev.user_id
        args: str = ev.message.extract_plain_text().strip().split()
        get_user_data(qqid)
        if not args:
            data = '请输入需要更新内容的参数'
        elif args[0] == 'mode':
            try:
                mode = int(args[1])
            except:
                await bot.finish('请输入更改的模式！')
            if mode >= 0 or mode < 4:
                result = update_user_mode(qqid, mode)
                if result:
                    data = f'已将默认模式更改为 {GameModeName[mode]}'
                else:
                    data = '数据库错误'
            else:
                data = '请输入正确的模式 0-3'
        else:
            data = '参数错误，请输入正确的参数'
    except UserNotBindError as e:
        data = str(e)
    await bot.send(data)


@sv.on_prefix(['osuhelp', 'Osuhelp', 'OSUHELP'])
async def osuhelp(bot: NoneBot, ev: CQEvent):
    await bot.send(ev, MessageSegment.image(f'file:///{static / "help.png"}'))


@sv.scheduled_job('cron', hour='0', minute='0')
async def update_info():
    num = await update_daily_data()
    sv.logger.info(f'已更新 {num} 位玩家数据')