import traceback
from datetime import datetime, timedelta
from time import mktime, strptime, time
from typing import List

from nonebot import MessageSegment
from PIL import Image, ImageDraw

from ... import *
from ..Api import osuApi
from ..Error import DrawImageError
from ..Model import Score
from ..Mods import Mods
from .Image import *


class DrawPerformance:
    
    def __init__(self, project: str, bplist: List[Score], setBpList: Union[List[int], range]) -> None:
        self.Project = project
        self.BPList = bplist
        self.setList = setBpList
        self.Username = bplist[0].user.username
        self.Mode = bplist[0].mode


    def draw_pfm(self) -> Image.Image:
        try:
            bg_img = Image.open(pfmbg).convert('RGBA')
            f_div = Image.new('RGBA', (1500, 2), (255, 255, 255, 255)).convert('RGBA')
            div = Image.new('RGBA', (1450, 2), (46, 53, 56, 255)).convert('RGBA')

            # 作图
            im = Image.new('RGBA', (1500, 180 + 82 * (len(self.setList) - 1)), (31, 41, 46, 255))
            # 字体
            text_im = ImageDraw.Draw(im)
            trfont = DrawText(text_im, TrFont)
            tsfont = DrawText(text_im, TsFont)
            mrfont = DrawText(text_im, MeiryoR)
            # 底图
            im.alpha_composite(bg_img)
            # 分割线
            im.alpha_composite(f_div, (0, 100))
            if self.Project == 'pfm':
                uinfo = f"{self.Username}'s | {self.Mode.capitalize()} | BP {self.setList.start + 1} - {self.setList.stop}"
            elif self.Project == 'tbp':
                uinfo = f"{self.Username}'s | {self.Mode.capitalize()} | Today New BP"
            else:
                uinfo = f"{self.Username}'s | {self.Mode.capitalize()} | Today Recent Plays"
            tsfont.draw(1450, 50, 25, uinfo, anchor='rm')
            for num, bp in enumerate(self.setList):
                h_num = 82 * num
                
                score = self.BPList[bp]
                # mods
                if score.mods:
                    for mods_num, s_mods in enumerate(score.mods):
                        mods_bg = ModsDir / f'{s_mods}.png'
                        mods_img = Image.open(mods_bg).convert('RGBA')
                        im.alpha_composite(mods_img, (1000 + 50 * mods_num, 126 + h_num))
                    if (score.rank == 'X' or score.rank == 'S') and ('HD' in score.mods or 'FL' in score.mods):
                        score.rank += 'H'
                # BP排名
                if self.Project != 'tr':
                    mrfont.draw(20, 143 + h_num, 20, bp + 1, anchor='mm')
                # rank
                rank_img = RankDir / f'ranking-{score.rank}.png'
                rank_bg = Image.open(rank_img).convert('RGBA').resize((64, 32))
                im.alpha_composite(rank_bg, (45, 128 + h_num))
                # 曲名&作曲
                mrfont.draw(125, 130 + h_num, 20, f'{score.beatmapset.title}  |  by {score.beatmapset.artist}', anchor='lm')
                # 地图版本
                x = trfont.get_box(score.beatmap.version, 18)
                trfont.draw(125, 158 + h_num, 18, score.beatmap.version, (238, 171, 0, 255), anchor='lm')
                # 时间
                trfont.draw(125 + x[2], 158 + h_num, 18, f'  |  {strtime(score.created_at)}', anchor='lm')
                # acc
                tsfont.draw(1250, 130 + h_num, 22, f'{score.accuracy * 100:.2f}%', (238, 171, 0, 255), anchor='lm')
                # mapid
                trfont.draw(1250, 158 + h_num, 18, f'ID: {score.beatmap.id}', anchor='lm')
                # pp
                tsfont.draw(1420, 140 + h_num, 25, round(score.pp) if score.pp != -1 else '--', (255, 102, 171, 255), anchor='rm')
                tsfont.draw(1450, 140 + h_num, 25, 'pp', (209, 148, 176, 255), anchor='rm')
                # 分割线
                im.alpha_composite(div, (25, 180 + h_num))

            return im
        except Exception as e:
            sv.logger.error(f'制图错误：{traceback.print_exc()}')
            raise DrawImageError(type(e))


def findTodayBp(scoreList: List[Score]) -> List[int]:
    tempList = []
    for index, value in enumerate(scoreList):
        today = datetime.now().date()
        today_stamp = mktime(strptime(str(today), '%Y-%m-%d'))
        playtime = datetime.strptime(value.created_at, '%Y-%m-%dT%H:%M:%SZ') + timedelta(hours=8)
        play_stamp = mktime(strptime(str(playtime), '%Y-%m-%d %H:%M:%S'))
        
        if play_stamp > today_stamp:
            tempList.append(index)

    return tempList


async def best_pfm(project: str, user_id: Union[str, int], mode: str, min: int = 0, max: int = 0, mods: List[str] = None) -> Union[str, MessageSegment]:  
    try:
        sv.logger.info(f'Start Request OsuAPI {playtime(time() * 1000)}')
        BPInfo = await osuApi.user_scores_best(user_id, mode=mode, limit=100)
        sv.logger.info(f'Ending Request OsuAPI {playtime(time() * 1000)}')
        if not BPInfo:
            return '未查询到游玩记录'
        
        BPList: List[Score] = []
        for score in BPInfo:
            BPList.append(Score(**score))
        
        if project == 'pfm':
            isr = False
            _range = None
            if min != 0 and max != 0:
                """指定范围"""
                _range = range(min, max)
                setBpList = _range
                isr = True
            if mods:
                indexList = Mods(BPList, mods).findModsIndex()
                if not indexList:
                    return f'未找到 {"|".join(mods)} Mods的成绩'
                if isr and len(_range) < len(indexList):
                    setBpList = indexList[min - 1, max]
                elif isr and len(_range) > len(indexList):
                    setBpList = indexList[min:]
                else:
                    setBpList = indexList
        elif project == 'tbp':
            setBpList = findTodayBp(BPList)
            if not setBpList:
                return f'今天没有新增的BP成绩'
        elif project == 'tr':
            setBpList = range(len(BPList))

        info = DrawPerformance(project, BPList, setBpList)
        im = info.draw_pfm()

        msg = MessageSegment.image(img2b64(im))
    except Exception as e:
        sv.logger.error(f'制图错误：{traceback.print_exc()}')
        msg = f'Error: {type(e)}'
    return msg