import traceback
from typing import List

from nonebot import MessageSegment
from PIL import ImageEnhance, ImageFilter

from ... import *
from ..Api import osuApi
from ..File import getImage
from ..Model import Beatmap, Sayomap
from ..Model.ScoreModel import Score, Statistics
from ..PP import PPCalc
from .Image import *


async def draw_map(mapid: int, mods: List[str]):
    try:
        info = await osuApi.beatmap(mapid)
        if not info:
            return '未查询到该地图信息'
        if isinstance(info, str): 
            return info
        map = Beatmap(**info)
        diffinfo = calc_songlen(map.total_length), map.bpm, map.count_circles, map.count_sliders
        # pp
        pp = await PPCalc(Score(
            accuracy=1,
            max_combo=map.max_combo,
            mode_int=map.mode_int,
            mods=mods,
            statistics=Statistics(
                count_100=0,
                count_300=0,
                count_50=0,
                count_geki=0,
                count_katu=0,
                count_miss=0,
            ),
            beatmap=map
        )).calc(isPlay=False)
        
        # 计算时间
        if map.beatmapset.ranked_date:
            new_time = strtime(map.beatmapset.ranked_date)
        else:
            new_time = '??-??-?? ??:??:??'

        bg = static / 'beatmapinfo.png'
        cover = await getImage(map.beatmapset.covers.cover2x)
        user_icon = await getImage(f'https://a.ppy.sh/{map.beatmapset.user_id}')

        bg_img = Image.open(bg).convert('RGBA')
        cover_img = ImageEnhance.Brightness(cropBG('MapBG', cover)).enhance(2 / 4.0)
        mode_img = starsDiff(map.mode_int, round(pp.StarRating, 2)).resize((50, 50))
        icon = Image.open(user_icon).convert('RGBA').resize((100, 100))
        
        # BG做地图
        im = Image.new('RGBA', (1200, 600))
        im.alpha_composite(cover_img)
        # 字体
        text_im = ImageDraw.Draw(im)
        trfont = DrawText(text_im, TrFont)
        tsfont = DrawText(text_im, TsFont)
        msfont = DrawText(text_im, MeiryoS)
        # 获取地图info
        im.alpha_composite(bg_img)
        # 模式
        im.alpha_composite(mode_img, (50, 100))
        # cs - diff
        if map.mode_int == 0:
            mapdiff = [round(map.cs, 1), round(map.drain, 1), round(pp.OD, 1), round(pp.AR, 1), round(pp.StarRating, 2)]
        else:
            mapdiff = [round(map.cs, 1), round(map.drain, 1), round(map.accuracy, 1), round(map.ar, 1), round(map.difficulty_rating, 2)]
        for num, i in enumerate(mapdiff):
            color = (255, 255, 255, 255)
            if num == 4:
                color = (255, 204, 34, 255)
            difflen = int(250 * i / 10) if i <= 10 else 250
            diff_len = Image.new('RGBA', (difflen, 8), color)
            im.alpha_composite(diff_len, (890, 426 + 35 * num))
            tsfont.draw(1170, 426 + 35 * num, 20, i, anchor='mm')
        # mapper
        im.alpha_composite(icon, (50, 400))
        # mapid
        tsfont.draw(800, 40, 22, f'Setid: {map.beatmapset_id}  |  Mapid: {mapid}', anchor='lm')
        # 版本
        tsfont.draw(120, 125, 25, map.version, anchor='lm')
        # 曲名
        msfont.draw(50, 170, 30, map.beatmapset.title_unicode or map.beatmapset.title)
        # 曲师
        msfont.draw(50, 210, 25, f'by {map.beatmapset.artist_unicode or map.beatmapset.artist}')
        # 来源
        msfont.draw(50, 260, 25, f'Source: {map.beatmapset.source}')
        # mapper
        tsfont.draw(160, 400, 20, 'mapper by:')
        tsfont.draw(160, 425, 20, map.beatmapset.creator)
        # ranked时间
        tsfont.draw(160, 460, 20, 'ranked by:')
        tsfont.draw(160, 485, 20, new_time)
        # 状态
        tsfont.draw(1100, 304, 20, map.beatmapset.status.capitalize(), anchor='mm')
        # 时长 - 滑条
        for num, i in enumerate(diffinfo):
            trfont.draw(770 + 120 * num, 365, 20, i, (255, 204, 34, 255), anchor='lm')
        # maxcb
        tsfont.draw(50, 570, 20, f'Max Combo: {map.max_combo}', anchor='lm')
        # pp
        tsfont.draw(320, 570, 20, f'SS PP: {round(pp.pp)}', anchor='lm')
        # 输出
        
        msg = MessageSegment.image(img2b64(im))
    except Exception as e:
        sv.logger.error(f'制图错误：{traceback.print_exc()}')
        msg = f'Error: {type(e)}'
    return msg


async def draw_beatmap(mapid: int, op: bool=False) -> Union[str, MessageSegment]:
    if op:
        info = await osuApi.beatmap(mapid)
        if not info:
            return '未查询到地图'
        elif isinstance(info, str):
            return info
        mapid = info['beatmapset_id']
    
    info = await osuApi.sayomap(mapid)
    if info['status'] == -1:
        return '未查询到地图'
    elif isinstance(info, str):
        return info
    
    try:
        map = Sayomap(**info['data'])
        cover = await getImage(f'https://assets.ppy.sh/beatmaps/{mapid}/covers/cover@2x.jpg')
        # 作图
        if (count := map.bids_amount) > 20:
            im_h = 400 + 102 * 20
        else:
            im_h = 400 + 102 * count if count < 5 else 5
        im = Image.new('RGBA', (1200, im_h), (31, 41, 46, 255))
        # 字体
        text_im = ImageDraw.Draw(im)
        tsfont = DrawText(text_im, TsFont)
        msfont = DrawText(text_im, MeiryoS)
        
        # 背景
        cover_crop = cropBG('BMapBG', cover)
        cover_gb = cover_crop.filter(ImageFilter.GaussianBlur(1))
        cover_img = ImageEnhance.Brightness(cover_gb).enhance(2 / 4.0)
        
        # 分割线
        div = Image.new('RGBA', (1150, 2), (46, 53, 56, 255)).convert('RGBA')
        im.alpha_composite(cover_img, (0, 0))
        # 曲名
        msfont.draw(25, 40, 38, map.titleU or map.title)
        # 曲师
        msfont.draw(25, 75, 20, f'by {map.artistU or map.artist}')
        # mapper
        tsfont.draw(25, 110, 20, f'mapper by {map.creator}')
        # rank时间
        if map.approved_date == -1:
            time = '??-??-?? ??:??:??'
        else:
            datearray = datetime.utcfromtimestamp(map.approved_date)
            time = (datearray + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
        tsfont.draw(25, 145, 20, f'Approved Time: {time}')
        # 来源
        msfont.draw(25, 180, 20, f'Source: {map.source}')
        # bpm
        tsfont.draw(1150, 110, 20, f'BPM: {map.bpm}', anchor='rt')
        # 曲长
        # music_len = calc_songlen(map)
        # tsfont.draw(1150, 145, 20, f'lenght: {music_len}', anchor='rt')
        # Setid
        tsfont.draw(1150, 20, 20, f'Setid: {map.sid}', anchor='rt')
        
        bar_img = Image.open(WorkDir / 'bmap.png').convert('RGBA')
        
        maplist = sorted(map.bid_data, key=lambda x: x.star, reverse=False)
        for num, beatmap in enumerate(maplist):
            if num < 20:
                h_num = 102 * num
                # 难度
                mode_bg = starsDiff(beatmap.mode, beatmap.star)
                mode_img = mode_bg.resize((20, 20))
                im.alpha_composite(mode_img, (20, 320 + h_num))
                # 星星
                stars_bg = starsDiff('stars', beatmap.star)
                stars_img = stars_bg.resize((20, 20))
                im.alpha_composite(stars_img, (50, 320 + h_num))
                # diff
                im.alpha_composite(bar_img, (10, 365 + h_num))
                gc = ['CS', 'HP', 'OD', 'AR']
                for num, i in enumerate([beatmap.CS, beatmap.HP, beatmap.OD, beatmap.AR]):
                    diff_len = int(200 * i / 10) if i <= 10 else 200
                    diff_bg = Image.new('RGBA', (diff_len, 12), (255, 255, 255, 255))
                    im.alpha_composite(diff_bg, (50 + 300 * num, 365 + h_num))
                    tsfont.draw(20 + 300 * num, 369 + h_num, 20, gc[num], anchor='lm')
                    tsfont.draw(265 + 300 * num, 369 + h_num, 20, i, (255, 204, 34, 255), anchor='lm')
                    if num != 3:
                        tsfont.draw(300 + 300 * num, 369 + h_num, 20, '|', anchor='lm')
                # 难度
                tsfont.draw(80, 328 + h_num, 20, beatmap.star, anchor='lm')
                # version
                tsfont.draw(125, 328 + h_num, 20, f' |  {beatmap.version}', anchor='lm')
                # mapid
                tsfont.draw(1150, 328 + h_num, 20, f'Mapid: {beatmap.bid}', anchor='rm')
                # maxcb
                tsfont.draw(700, 328 + h_num, 20, f'Max Combo: {beatmap.maxcombo}', anchor='lm')
                # 分割线
                im.alpha_composite(div, (25, 400 + h_num))
            else:
                plusnum = f'+ {num - 19}'
        if num >= 20:
            tsfont.draw(600, 350 + 102 * 20, 50, plusnum, anchor='mm')

        msg = MessageSegment.image(img2b64(im))
    except Exception as e:
        sv.logger.error(f'制图错误：{traceback.print_exc()}')
        msg = f'Error: {type(e)}'
    return msg