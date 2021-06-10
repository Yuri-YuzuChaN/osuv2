from hoshino.config import SUPERUSERS
from hoshino import Service, priv
from hoshino.typing import CQEvent
from nonebot import get_bot
import re, os

from .sql import *
from .draw import *
from .file import MapDownload
from .api import get_access_token
from .mods import get_mods_num

sv = Service('osuv2', manage_priv=priv.ADMIN, enable_on_default=True)
helpimg = os.path.join(os.path.dirname(__file__), 'osufile', 'help.png')

GM = {0 : 'osu', 1 : 'taiko', 2 : 'fruits', 3 : 'mania'}
GMN = {0 : 'Std', 1 : 'Taiko', 2 : 'Ctb', 3 : 'Mania'}
esql = osusql()

@sv.on_prefix(('info', 'INFO', 'Info'))
async def info(bot, ev:CQEvent):
    msg = ev.message
    if msg[0]['type'] == 'text':
        uid = ev.user_id
        result = esql.get_id_mod(uid)
        text = msg[0]['data']['text']
        if not text:
            if not result:
                await bot.finish(ev, '该账号尚未绑定，请输入 bind 用户名 绑定账号', at_sender=True)
            for i in result:
                id = i[0]
                mode = i[1]
        else:
            msglist = text.strip().split(' ')
            while '' in msglist:
                msglist.remove('')
            mlen = len(msglist)
            if ':' in msglist[-1] and mlen == 1:
                if not result:
                    await bot.finish(ev, '该账号尚未绑定，请输入 bind 用户名 绑定账号', at_sender=True)
                for i in result:
                    id = i[0]
                    mode = int(msglist[-1][1])
            elif ':' in msglist[-1]:
                id = ' '.join(msglist[:mlen-1])
                mode = int(msglist[-1][1])
            else:
                id = ' '.join(msglist[:mlen])
                mode = 0
    elif msg[0]['type'] == 'at':
        uid = int(msg[0]['data']['qq'])
        result = esql.get_id_mod(uid)
        if not result:
            await bot.finish(ev, '该账号尚未绑定，请输入 bind 用户名 绑定账号', at_sender=True)
        if len(msg) == 2:
            if msg[1]['data']['text'].isspace():
                msg.pop(1)
        if len(msg) == 1:
            for i in result:
                id = i[0]
                mode = i[1]
        elif msg[1]['type'] == 'text':
            text = msg[1]['data']['text'].strip()
            if ':' in text and text[1].isdigit():
                for i in result:
                    id = i[0]
                mode = int(text[1])
            else:
                await bot.finish(ev, '模式错误', at_sender=True)
        else:
            await bot.finish(ev, '指令错误', at_sender=True)
    else:
        await bot.finish(ev, '指令错误', at_sender=True)

    info = await draw_info(id, GM[mode])
    await bot.send(ev, info, at_sender=True)

@sv.on_prefix(('recent', 're', 'RECENT', 'RE', 'Recent', 'Re'))
async def recent(bot, ev:CQEvent):
    msg = ev.message
    if msg[0]['type'] == 'text':
        uid = ev.user_id
        result = esql.get_id_mod(uid)
        text = msg[0]['data']['text']
        if not text:
            if not result:
                await bot.finish(ev, '该账号尚未绑定，请输入 bind 用户名 绑定账号', at_sender=True)
            for i in result:
                id = i[0]
                mode = i[1]
        else:
            msglist = text.strip().split(' ')
            while '' in msglist:
                msglist.remove('')
            mlen = len(msglist)
            if ':' in msglist[-1] and mlen == 1:
                if not result:
                    await bot.finish(ev, '该账号尚未绑定，请输入 bind 用户名 绑定账号', at_sender=True)
                for i in result:
                    id = i[0]
                    mode = int(msglist[-1][1])
            elif ':' in msglist[-1]:
                id = ' '.join(msglist[:mlen-1])
                mode = int(msglist[-1][1])
            else:
                id = ' '.join(msglist[:mlen])
                mode = 0
    elif msg[0]['type'] == 'at':
        uid = int(msg[0]['data']['qq'])
        result = esql.get_id_mod(uid)
        if not result:
            await bot.finish(ev, '该账号尚未绑定，请输入 bind 用户名 绑定账号', at_sender=True)
        if len(msg) == 2:
            if msg[1]['data']['text'].isspace():
                msg.pop(1)
        if len(msg) == 1:
            for i in result:
                id = i[0]
                mode = i[1]
        elif msg[1]['type'] == 'text':
            text = msg[1]['data']['text'].strip()
            if ':' in text and text[1].isdigit():
                for i in result:
                    id = i[0]
                mode = int(text[1])
            else:
                await bot.finish(ev, '模式错误', at_sender=True)
        else:
            await bot.finish(ev, '指令错误', at_sender=True)
    else:
        await bot.finish(ev, '指令错误', at_sender=True)
    
    info = await draw_score('recent', id, GM[mode])
    await bot.send(ev, info, at_sender=True)

@sv.on_prefix(('score', 'SCORE', 'Score'))
async def score(bot, ev:CQEvent):
    msg = ev.message
    if msg[0]['type'] == 'text':
        text = msg[0]['data']['text'].strip().split(' ')
        while '' in text:
            text.remove('')
        if not text:
            await bot.finish(ev, '请输入正确的地图ID', at_sender=True)
        uid = ev.user_id
        result = esql.get_id_mod(uid)
        if len(text) == 1:
            if not result:
                await bot.finish(ev, '该账号尚未绑定，请输入 bind 用户名 绑定账号', at_sender=True)
            elif text[0].isdigit():
                for i in result:
                    id = i[0]
                mode = 0
                mapid = text[0]
            else:
                await bot.finish(ev, '请输入正确的地图ID', at_sender=True)
        elif len(text) == 2:
            if ':' in text[-1] and text[0].isdigit():
                if not result:
                    await bot.finish(ev, '该账号尚未绑定，请输入 bind 用户名 绑定账号', at_sender=True)
                for i in result:
                    id = i[0]
                mapid = text[0]
                mode = int(text[-1][1])
            elif text[-1].isdigit():
                id = text[0]
                mapid = text[-1]
                mode = 0
            else:
                await bot.finish(ev, '请输入正确的地图ID', at_sender=True)
        else:
            if ':' in text[-1] and text[-2].isdigit():
                id = ' '.join(text[:len(text)-2])
                mapid = text[-2]
                mode = int(text[-1][1])
            elif text[-1].isdigit():
                id = ' '.join(text[:len(text)-1])
                mapid = text[-1]
                mode = 0
            else:
                await bot.finish(ev, '请输入正确的地图ID', at_sender=True)
    elif msg[0]['type'] == 'at':
        if len(msg) == 1:
            await bot.finish(ev, '请输入正确的地图ID', at_sender=True)
        uid = int(msg[0]['data']['qq'])
        result = esql.get_id_mod(uid)
        if not result:
            await bot.finish(ev, '该账号尚未绑定，请输入 bind 用户名 绑定账号', at_sender=True)
        if msg[1]['type'] == 'text':
            text = msg[1]['data']['text'].strip().split(' ')
            while '' in text:
                text.remove('')
            if not text:
                await bot.finish(ev, '请输入正确的地图ID', at_sender=True)
            for i in result:
                id = i[0]
            if ':' in text[-1] and text[0].isdigit():
                mapid = text[0]
                mode = int(text[-1][1])
            elif text[0].isdigit():
                mapid = text[0]
                mode = 0
            else:
                await bot.finish(ev, '请输入正确的地图ID', at_sender=True)
        else:
            await bot.finish(ev, '指令错误', at_sender=True)
    else:
        await bot.finish(ev, '请输入正确的地图ID', at_sender=True)
    
    info = await draw_score('score', id, GM[mode], mapid=mapid)
    await bot.send(ev, info, at_sender=True)

@sv.on_prefix(('bp', 'BP', 'Bp'))
async def bp(bot, ev:CQEvent):
    uid = ev.user_id
    msg = ev.message.extract_plain_text().strip().split(' ')
    mode = 0
    mods = 0
    bp = ''
    while '' in msg:
        msg.remove('')
    if not msg:
        await bot.finish(ev, '请输入正确的参数', at_sender=True)
    elif 'CQ:at' in str(ev.message):
        result = re.finditer(r'\[CQ:at,qq=(.*)\]', str(ev.message))
        for i in result:
            uid = int(i.groups()[0])
    if '+' in msg[-1]:
        msg[-1] = msg[-1].upper()
        mods = msg[-1][1:].split(',')
        del msg[-1]
    if len(msg) != 1:
        if msg[0] == '1' or msg[0] == '2' or msg[0] == '3':
            mode = int(msg[0])
            del msg[0]
    result = esql.get_name_mod(uid)
    msg_len = len(msg)
    if '-' in msg[-1]:
        lr = re.match(r'(.*)-(.*)', msg[-1])
        try:
            min, max = int(lr.group(1)), int(lr.group(2))
        except:
            await bot.finish(ev, '请输入正确的bp范围', at_sender=True)
        if min > 50 or max > 50:
            await bot.finish(ev, '只允许查询bp 1-50 的成绩', at_sender=True)
        if msg_len == 1:
            if not result:
                await bot.finish(ev, '该账号尚未绑定，请输入 bind 用户名 绑定账号', at_sender=True)
            for i in result:
                id = i[0]
            range_limit = max - min + 1
            if min >= max:
                await bot.finish(ev, '请输入正确的bp范围', at_sender=True)
            elif range_limit > 10:
                await bot.finish(ev, '只允许查询10个bp成绩', at_sender=True)
        else:
            range_limit = max - min +1
            if min >= max:
                await bot.finish(ev, '请输入正确的bp范围', at_sender=True)
            elif range_limit > 10:
                await bot.finish(ev, '只允许查询10个bp成绩', at_sender=True)
            id = ' '.join(msg[:-1])
    elif msg_len == 1:
        if not result:
            await bot.finish(ev, '该账号尚未绑定，请输入 bind 用户名 绑定账号', at_sender=True)
        elif msg[0].isdigit() and result:
            for i in result:
                id = i[0]
            if int(msg[0]) <= 0 or int(msg[0]) > 50:
                await bot.finish(ev, '只允许查询bp 1-50 的成绩', at_sender=True)
            bp = int(msg[0])
        else:
            await bot.finish(ev, '请输入正确的参数', at_sender=True)
    elif msg_len >= 2:
        if msg[-1].isdigit():
            id = ' '.join(msg[:msg_len-1])
            if int(msg[-1]) <= 0 or int(msg[-1]) > 50:
                await bot.finish(ev, '只允许查询bp 1-50 的成绩', at_sender=True)
            bp = int(msg[-1])
        else:
            await bot.finish(ev, '请输入正确的参数', at_sender=True)   
    if bp:
        if mods != 0:
            info = await draw_score('bp', id, GM[mode], bp=bp, mods=mods)
        else:
            info = await draw_score('bp', id, GM[mode], bp=bp)
    else:
        if mods !=0 :
            info = await best_pfm(id, GM[mode], min, max, mods)
        else:
            info = await best_pfm(id, GM[mode], min, max)
    
    await bot.send(ev, info, at_sender=True)
    
@sv.on_prefix(('map', 'MAP', 'Map'))
async def map(bot, ev:CQEvent):
    mapid = ev.message.extract_plain_text().strip().split(' ')
    mods = 0
    while '' in mapid:
        mapid.remove('')
    if not mapid:
        await bot.finish(ev, '请输入地图ID', at_sender=True)
    elif not mapid[0].isdigit():
        await bot.finish(ev, '请输入正确的地图ID', at_sender=True)
    if '+' in mapid[-1]:
        mods = get_mods_num(mapid[-1][1:].split(','))
        del mapid[-1]
    info = await map_info(mapid[0], mods)
    if isinstance(info, tuple): 
        for msg in info:
            await bot.send(ev, msg)
    else:
        await bot.send(ev, info, at_sender=True)

@sv.on_prefix(('smap', 'SMAP', 'Smap'))
async def search(bot, ev:CQEvent):
    word = ev.message.extract_plain_text().strip().split(' ')
    mode = 0
    status = 0
    op = 's'
    while '' in word:
        word.remove('')
    if not word:
        await bot.finish(ev, '请输入查询地图的关键词', at_sender=True)
    elif word[0] == '1' or word[0] == '2' or word[0] == '3':
        if word[1].lower() == '-s' or word[1].lower() == '-c':
            op = word[1][1:]
            del word[1]
        mode = int(word[0])
        del word[0]
    elif word[0].lower() == '-s' or word[0].lower() == '-c':
        op = word[0][1:]
        del word[0]
    if op == 's':
        op = False
    elif op == 'c':
        op = True
    else:
        await bot.finish(ev, '请输入正确的搜索引擎', at_sender=True)
    if 'rs=' in word[-1]:
        try:
            status = int(word[-1][3:])
            if status > 0 and status < 6:
                del word[-1]
            else:
                await bot.finish(ev, '请输入正确的rank状态', at_sender=True)
        except:
            await bot.finish(ev, '请输入正确的rank状态', at_sender=True)
    keyword = " ".join(word)
    info = await search_map('search', mode, status, keyword, op)
    await bot.send(ev, info)

@sv.on_prefix(('bmap', 'BMAP', 'Bmap'))
async def bmap(bot, ev:CQEvent):
    msg = ev.message.extract_plain_text().strip().split(' ')
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
    setid = ev.message.extract_plain_text().strip()
    if not setid:
        return
    if not setid.isdigit():
        await bot.finish(ev, '请输入正确的地图ID', at_sender=True)
    file = await MapDownload(setid, True)
    await bot.upload_group_file(group_id=gid, file=file[0], name=file[1])
    os.remove(file[0])

@sv.on_prefix(('bind', 'BIND', 'Bind'))
async def bind(bot, ev:CQEvent):
    uid = ev.user_id
    id = ev.message.extract_plain_text()
    if not id:
        await bot.finish(ev, '请输入您的 osuid', at_sender=True)
    result = esql.get_name_mod(uid)
    if result:
        await bot.finish(ev, '您已绑定，如需要解绑请输入unbind', at_sender=True)
    msg = await bindinfo('bind', id, uid)
    await bot.send(ev, msg, at_sender=True)

@sv.on_prefix(('unbind', 'Unbind', 'UNBIND'))
async def unbind(bot, ev:CQEvent):
    uid = ev.user_id
    sel_result = esql.get_id_mod(uid)
    if sel_result: 
        del_result = esql.delete_user(uid)
        if del_result:
            await bot.send(ev, '解绑成功！', at_sender=True)
            esql.delete_newinfo(sel_result[0][0])
        else:
            await bot.send(ev, '数据库错误')
    else:
        await bot.send(ev, '尚未绑定，无需解绑', at_sender=True)

@sv.on_prefix(('update', 'UPDATE', 'Update'))
async def recent(bot, ev:CQEvent):
    uid = ev.user_id
    msg = ev.message.extract_plain_text().strip().split(' ')
    while '' in msg:
        msg.remove('')
    result = esql.get_id_mod(uid)
    if not result:
        botmsg = '该账号尚未绑定，请输入 bind 用户名 绑定账号'
    elif not msg:
        botmsg = '请输入需要更新内容的参数'
    elif msg[0] == 'mode':
        try:
            mode = int(msg[1])
        except:
            await bot.finish(ev, '请输入更改的模式！', at_sender=True)
        if mode >= 0 or mode < 4:
            result = esql.update_mode(uid, mode)
            if result:
                botmsg = f'已将默认模式更改为 {GMN[mode]}'
            else:
                botmsg = '数据库错误'
        else:
            botmsg = '请输入正确的模式 0-3'
    elif msg[0] == 'icon':
        for i in result:
            id = i[0]
            mode = i[1]
        botmsg = await update_icon('update', id, GM[mode])
    else:
        botmsg = '参数错误，请输入正确的参数'
    await bot.send(ev, botmsg, at_sender=True)

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
    await bot.send(ev, f'[CQ:image,file=file:///{helpimg}]')

@sv.scheduled_job('cron', hour='23')
async def refresh_token_():
    msg = await get_access_token()
    bot = get_bot()
    for user_id in SUPERUSERS:
        await bot.send_msg(user_id=user_id, message=msg)

@sv.scheduled_job('cron', hour='0')
async def update_info():
    result = esql.get_all_id()
    for n, uid in enumerate(result):
        await user(uid[0], True)
    hoshino.logger.info(f'已更新{n+1}位玩家数据')
