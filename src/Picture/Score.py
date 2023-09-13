import gc
import os
import traceback
from time import time
from typing import List, Optional

from matplotlib.figure import Figure
from nonebot import MessageSegment
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from ... import *
from ..Api import osuApi
from ..Error import DrawImageError
from ..File import *
from ..Model import Beatmap, BestScore, Score, User
from ..PP import *
from .Image import *


class DrawScore:
    
    def __init__(self, project: str, scoreData: Union[Score, BestScore]) -> None:
        self.Project = project
        if self.Project == 'score':
            self.GRank = scoreData.position
            self.score: Score = scoreData.score
            self.user: User = scoreData.score.user
        else:
            self.score: Score = scoreData
            self.user: User = scoreData.user
        self.beatmap = self.score.beatmap
    
    
    def loadMap(self, map: Beatmap) -> None:
        """ 使用 `score` 指令时需要另外获取地图数据 """
        self.beatmap = map
    
    
    def _wedgeAcc(self) -> BytesIO:
        size = [self.score.accuracy * 100, 100 - self.score.accuracy * 100]
        insize = [60, 20, 7, 7, 5, 1]
        insizecolor = ['#ff5858', '#ea7948', '#d99d03', '#72c904', '#0096a2', '#be0089']
        fig = Figure()
        ax = fig.add_axes((0.1, 0.1, 0.8, 0.8))
        patches = ax.pie(size, radius=1.1, startangle=90, counterclock=False, pctdistance=0.9, wedgeprops=dict(width=0.27))
        ax.pie(insize, radius=0.8, colors=insizecolor, startangle=90, counterclock=False, pctdistance=0.9, wedgeprops=dict(width=0.05))
        patches[0][1].set_alpha(0)
        img = BytesIO()
        fig.savefig(img, transparent=True)
        ax.cla()
        ax.clear()
        fig.clf()
        fig.clear()
        gc.collect()
        return img
    
    
    async def draw(self) -> Image.Image:
        try:
            if self.Project != 'score':
                self.GRank = '--'

            ppcalc = PPCalc(self.score)
            pp = await ppcalc.calc()
            
            if self.score.mode_int != 0:
                od = round(self.beatmap.accuracy, 1)
                ar = round(self.beatmap.ar, 1)
                self.stars = self.beatmap.difficulty_rating
            else:
                od = round(pp.OD, 1)
                ar = round(pp.AR, 1)
                self.stars = round(pp.StarRating, 2)

            if 'HD' in self.score.mods or 'FL' in self.score.mods:
                ranking = ['XH', 'SH', 'A', 'B', 'C', 'D', 'F']
            else:
                ranking = ['X', 'S', 'A', 'B', 'C', 'D', 'F']
            
            cover = await getImage(self.beatmap.beatmapset.covers.cover2x)
            cover_img = ImageEnhance.Brightness(cropBG('BG', cover).filter(ImageFilter.GaussianBlur(1))).enhance(2 / 4.0)
            bg_img = Image.open(bgImg[self.score.mode_int]).convert('RGBA')
            mode_img = starsDiff(self.score.mode_int, self.stars).resize((30, 30))
            stars_img = starsDiff(self.score.mode_int, self.stars).resize((23, 23))
            score_acc_img = Image.open(self._wedgeAcc()).convert('RGBA').resize((576, 432))
            icon = Image.open(await getImage(self.user.avatar_url)).convert('RGBA').resize((150, 150))
            icon_img = draw_filler(icon, 25)
            country_img = Image.open(os.path.join(FlagsDir, f'{self.user.country_code}.png')).convert('RGBA').resize((58, 39))
            status_img = Image.open(os.path.join(WorkDir, 'on-line.png' if self.user.is_online else 'off-line.png')).convert('RGBA').resize((45, 45))
            supporter_img = Image.open(os.path.join(WorkDir, 'suppoter.png')).convert('RGBA').resize((40, 40))
            
            # 作图
            im = Image.new('RGBA', (1500, 800))
            # 字体
            text_im = ImageDraw.Draw(im)
            trfont = DrawText(text_im, TrFont)
            tsfont = DrawText(text_im, TsFont)
            msfont = DrawText(text_im, MeiryoS)
            vfont = DrawText(text_im, Venera)
            # 曲绘
            im.alpha_composite(cover_img, (0, 200))
            # 底图
            im.alpha_composite(bg_img)
            # 模式
            im.alpha_composite(mode_img, (75, 154))
            # 星级
            im.alpha_composite(stars_img, (134, 158))
            # Mods
            if self.score.mods:
                for num, s in enumerate(self.score.mods):
                    mods_img = Image.open(os.path.join(ModsDir, f'{s}.png')).convert('RGBA')
                    im.alpha_composite(mods_img, (500 + 50 * num, 240))
            # 游玩评价
            rank_ok = False
            for num, i in enumerate(ranking):
                rank_img = os.path.join(RankDir, f'ranking-{i}.png')
                rank_b = Image.open(rank_img).resize((48, 24))
                if rank_ok:
                    rank_new = Image.new('RGBA', rank_b.size, (0, 0, 0, 0))
                    rank_bg = Image.blend(rank_new, rank_b, 0.5)
                elif i != self.score.rank:
                    rank_new = Image.new('RGBA', rank_b.size, (0, 0, 0, 0))
                    rank_bg = Image.blend(rank_new, rank_b, 0.2)
                else:
                    rank_bg = rank_b
                    rank_ok = True
                im.alpha_composite(rank_bg, (75, 243 + 39 * num))
            # Acc作图
            im.alpha_composite(score_acc_img, (15, 153))
            # 头像
            im.alpha_composite(icon_img, (50, 606))
            # 地区
            im.alpha_composite(country_img, (230, 606))
            # 状态
            im.alpha_composite(status_img, (230, 712))
            # supporter
            if self.user.is_supporter:
                im.alpha_composite(supporter_img, (300, 606))
            # 地图难度
            if self.score.mode_int == 0:
                mapdiff = [self.beatmap.cs, self.beatmap.drain, od, ar, self.stars]
            else:
                mapdiff = [self.beatmap.cs, self.beatmap.drain, self.beatmap.accuracy, self.beatmap.ar, self.stars]
            for num, i in enumerate(mapdiff):
                color = (255, 204, 34, 255) if num == 4 else (255, 255, 255, 255)
                len = int(250 * i / 10) if i <= 10 else 250
                im.alpha_composite(Image.new('RGBA', (len, 8), color), (1190, 386 + 35 * num))
                tsfont.draw(1470, 386 + 35 * num, 20, i, anchor='mm')
            # 地图数据
            for num, i in enumerate([calc_songlen(self.beatmap.total_length), self.beatmap.bpm, self.beatmap.count_circles, self.beatmap.count_sliders]):
                trfont.draw(1070 + 120 * num, 325, 20, i, (255, 204, 34, 255), anchor='lm')
            # 地图状态
            tsfont.draw(1400, 264, 20, self.beatmap.beatmapset.status.capitalize(), anchor='mm')
            # ID
            tsfont.draw(1425, 40, 27, f'Setid: {self.beatmap.beatmapset_id}  |  Mapid: {self.beatmap.id}', anchor='rm')
            # 标题和曲师
            msfont.draw(75, 118, 30, f'{self.beatmap.beatmapset.title_unicode} | by {self.beatmap.beatmapset.artist_unicode}', anchor='lm')
            # 星数
            tsfont.draw(162, 169, 18, self.stars, anchor='lm')
            # 版本
            tsfont.draw(225, 169, 22, f'{self.beatmap.version} | mapper by {self.beatmap.beatmapset.creator}', anchor='lm')
            # 评价
            vfont.draw(309, 375, 75, self.score.rank, anchor='mm')
            # 分数
            trfont.draw(498, 331, 75, f'{self.score.score:,}', anchor='lm')
            # 玩家名
            tsfont.draw(498, 396, 18, 'Played by:', anchor='lm')
            tsfont.draw(630, 396, 18, self.user.username, anchor='lm')
            # 游玩时间
            tsfont.draw(498, 421, 18, 'Submitted on:', anchor='lm')
            tsfont.draw(630, 421, 18, strtime(self.score.created_at), anchor='lm')
            # 全球排名
            tsfont.draw(513, 496, 24, self.GRank, anchor='lm')
            # 玩家名
            tsfont.draw(230, 670, 24, self.user.username, anchor='lm')
            # 在线状态
            tsfont.draw(300, 732, 30, 'online' if self.user.is_online else 'offline', anchor='lm')
            # 游玩信息
            if self.score.mode_int == 0:
                trfont.draw(650, 625, 30, round(pp.sspp), anchor='mm')
                trfont.draw(770, 625, 30, round(pp.ifpp), anchor='mm')
                trfont.draw(890, 625, 30, round(pp.pp), anchor='mm')
                trfont.draw(650, 720, 30, round(pp.aim), anchor='mm')
                trfont.draw(770, 720, 30, round(pp.speed), anchor='mm')
                trfont.draw(890, 720, 30, round(pp.accuracy), anchor='mm')
                trfont.draw(1087, 625, 30, f'{self.score.accuracy * 100:.2f}%', anchor='mm')
                trfont.draw(1315, 625, 30, f'{self.score.max_combo:,}/{self.beatmap.max_combo:,}', anchor='mm')
                trfont.draw(1030, 720, 30, self.score.statistics.count_300, anchor='mm')
                trfont.draw(1144, 720, 30, self.score.statistics.count_100, anchor='mm')
                trfont.draw(1258, 720, 30, self.score.statistics.count_50, anchor='mm')
                trfont.draw(1372, 720, 30, self.score.statistics.count_miss, anchor='mm')
            elif self.score.mode_int == 1:
                trfont.draw(1050, 625, 30, f'{self.score.accuracy * 100:.2f}%', anchor='mm')
                trfont.draw(1202, 625, 30, f'{self.score.max_combo:,}/{self.beatmap.max_combo:,}', anchor='mm')
                trfont.draw(1352, 625, 30, f'{round(pp.pp)}/{round(pp.ifpp)}', anchor='mm')
                trfont.draw(1050, 720, 30, self.score.statistics.count_300, anchor='mm')
                trfont.draw(1202, 720, 30, self.score.statistics.count_100, anchor='mm')
                trfont.draw(1352, 720, 30, self.score.statistics.count_miss, anchor='mm')
            elif self.score.mode_int == 2:
                trfont.draw(1016, 625, 30, f'{self.score.accuracy * 100:.2f}%', anchor='mm')
                trfont.draw(1180, 625, 30, f'{self.score.max_combo:,}/{self.beatmap.max_combo:,}', anchor='mm')
                trfont.draw(1344, 625, 30, f'{round(pp.pp)}/{round(pp.ifpp)}', anchor='mm')
                trfont.draw(995, 720, 30, self.score.statistics.count_300, anchor='mm')
                trfont.draw(1118, 720, 30, self.score.statistics.count_100, anchor='mm')
                trfont.draw(1242, 720, 30, self.score.statistics.count_katu, anchor='mm')
                trfont.draw(1365, 720, 30, self.score.statistics.count_miss, anchor='mm')
            else:
                trfont.draw(935, 625, 30, f'{self.score.accuracy * 100:.2f}%', anchor='mm')
                trfont.draw(1130, 625, 30, f'{self.score.max_combo:,}', anchor='mm')
                trfont.draw(1328, 625, 30, f'{round(pp.pp)}/{round(pp.ifpp)}', anchor='mm')
                trfont.draw(886, 720, 30, self.score.statistics.count_geki, anchor='mm')
                trfont.draw(984, 720, 30, self.score.statistics.count_300, anchor='mm')
                trfont.draw(1083, 720, 30, self.score.statistics.count_katu, anchor='mm')
                trfont.draw(1182, 720, 30, self.score.statistics.count_100, anchor='mm')
                trfont.draw(1280, 720, 30, self.score.statistics.count_50, anchor='mm')
                trfont.draw(1378, 720, 30, self.score.statistics.count_miss, anchor='mm')

            return im
        except PPError as e:
            raise PPError
        except Exception as e:
            sv.logger.error(f'制图错误：{traceback.print_exc()}')
            raise DrawImageError(type(e))
        
async def draw_score(project: str, user_id: str, mode: str, *, mapid: Optional[int] = 0, best: Optional[int] = 0, mods: List[str] = None) -> Union[str, MessageSegment]:
    try:
        sv.logger.info(f'Start Request OsuAPI {playtime(time() * 1000)}')
        if project == 'score':
            data = await osuApi.user_scores(user_id, mapid, mode=mode, mods=mods)
            scoreData = BestScore(**data)
        else:
            data = await osuApi.user_scores_best(user_id, mode=mode, limit=100)
            scoreData = Score(**data[best - 1])

        ds = DrawScore(project, scoreData)
        mapJson = await osuApi.beatmap(ds.beatmap.id)
        ds.loadMap(Beatmap(**mapJson))
        sv.logger.info(f'Ending Request OsuAPI {playtime(time() * 1000)}')

        im = await ds.draw()
        msg = MessageSegment.image(img2b64(im))
    except Exception as e:
        sv.logger.error(f'制图错误：{traceback.print_exc()}')
        msg = f'Error: {type(e)}'
    return msg