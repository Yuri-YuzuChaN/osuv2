from nonebot import MessageSegment
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from datetime import datetime, timedelta
from io import BytesIO, TextIOWrapper
from typing import Union, Optional, List, Tuple
from time import strftime, strptime, localtime, time, mktime

import os, math, traceback, base64, gc
from matplotlib.figure import Figure

from . import *
from .api import osu_api, SayoApi
from .file import *
from .pp import *
from .mods import *
from .sql import USER
from .data import SayoInfo,  Beatmapset
from .error import *

CROP_SIZE = {
    'BG': [1500, 360],
    'Header': [1000, 400],
    'MAPBG': [1200, 600],
    'BMAPBG': [1200, 300]
}
Torus_Regular = os.path.join(FILEPATH, 'fonts', 'Torus Regular.otf')
Torus_SemiBold = os.path.join(FILEPATH, 'fonts', 'Torus SemiBold.otf')
Meiryo_Regular = os.path.join(FILEPATH, 'fonts', 'Meiryo Regular.ttf')
Meiryo_SemiBold = os.path.join(FILEPATH, 'fonts', 'Meiryo SemiBold.ttf')
Venera = os.path.join(FILEPATH, 'fonts', 'Venera.otf')

def get_mode_image(mode: str) -> str:
    if mode == 0:
        img = 'pfm_std.png'
    elif mode == 1:
        img = 'pfm_taiko.png'
    elif mode == 2:
        img = 'pfm_ctb.png'
    else:
        img = 'pfm_mania.png'
    return os.path.join(FILEPATH, img)

def draw_filler(img: Image.Image, radii: int) -> Image.Image:
    # 画圆（用于分离4个角）
    circle = Image.new('L', (radii * 2, radii * 2), 0)  # 创建一个黑色背景的画布
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radii * 2, radii * 2), fill=255)  # 画白色圆形
    # 原图
    img = img.convert("RGBA")
    w, h = img.size
    # 画4个角（将整圆分离为4个部分）
    alpha = Image.new('L', img.size, 255)
    alpha.paste(circle.crop((0, 0, radii, radii)), (0, 0))  # 左上角
    alpha.paste(circle.crop((radii, 0, radii * 2, radii)), (w - radii, 0))  # 右上角
    alpha.paste(circle.crop((radii, radii, radii * 2, radii * 2)), (w - radii, h - radii))  # 右下角
    alpha.paste(circle.crop((0, radii, radii, radii * 2)), (0, h - radii))  # 左下角
    # 白色区域透明可见，黑色区域不可见
    img.putalpha(alpha)
    return img

def wedge_acc(acc: float) -> Image.Image:
    size = [acc, 100 - acc]
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

def crop_bg(size: str, path: Union[str, BytesIO]) -> Image.Image:
    bg = Image.open(path).convert('RGBA')
    bg_w, bg_h = bg.size[0], bg.size[1]
    fix_w, fix_h = CROP_SIZE[size]
    #固定比例
    fix_scale = fix_h / fix_w
    #图片比例
    bg_scale = bg_h / bg_w
    #当图片比例大于固定比例
    if bg_scale > fix_scale:
        #长比例
        scale_width = fix_w / bg_w
        #等比例缩放
        width = int(scale_width * bg_w)
        height = int(scale_width * bg_h)
        sf = bg.resize((width, height))
        #计算上下裁切
        crop_height = (height - fix_h) / 2
        x1, y1, x2, y2 = 0, crop_height, width, height - crop_height
        #裁切保存
        crop_img = sf.crop((x1, y1, x2, y2))
        return crop_img
    #当图片比例小于固定比例
    elif bg_scale < fix_scale:
        #宽比例
        scale_height = fix_h / bg_h
        #等比例缩放
        width = int(scale_height * bg_w)
        height = int(scale_height * bg_h)
        sf = bg.resize((width, height))
        #计算左右裁切
        crop_width = (width - fix_w) / 2
        x1, y1, x2, y2 = crop_width, 0, width - crop_width, height
        #裁切保存
        crop_img = sf.crop((x1, y1, x2, y2))
        return crop_img
    else:
        sf = bg.resize((fix_w, fix_h))
        return sf

def stars_diff(mode: str, stars: float) -> Image.Image:
    if mode == 0:
        mode = 'std'
    elif mode == 1:
        mode = 'taiko'
    elif mode == 2:
        mode = 'ctb'
    elif mode == 3:
        mode = 'mania'
    else:
        mode = 'stars'
    default = 115
    if stars < 1:
        xp = 0
        default = 120
    elif stars < 2:
        xp = 120
        default = 120
    elif stars < 3:
        xp = 240
    elif stars < 4:
        xp = 355
    elif stars < 5:
        xp = 470
    elif stars < 6:
        xp = 585
    elif stars < 7:
        xp = 700
    elif stars < 8:
        xp = 815
    else:
        return Image.open(os.path.join(FILEPATH, 'work', f'{mode}_expertplus.png')).convert('RGBA')
    # 取色
    x = (stars - math.floor(stars)) * default + xp
    color = Image.open(os.path.join(FILEPATH, 'work', 'color.png')).load()
    r, g, b = color[x, 1]
    # 打开底图
    im = Image.open(os.path.join(FILEPATH, 'work', f'{mode}.png')).convert('RGBA')
    xx, yy = im.size
    # 填充背景
    sm = Image.new('RGBA', im.size, (r, g, b))
    sm.paste(im, (0, 0, xx, yy), im)
    # 把白色变透明
    for i in range(xx):
        for z in range(yy):
            data = sm.getpixel((i, z))
            if (data.count(255) == 4):
                sm.putpixel((i, z), (255, 255, 255, 0))
    return sm

class DrawText:

    def __init__(self, image: ImageDraw.ImageDraw, font: str) -> None:
        self._img = image
        self._font = font

    def get_box(self, text: str, size: int):
        return ImageFont.truetype(self._font, size).getbbox(text)

    def draw(self,
            pos_x: int,
            pos_y: int,
            size: int,
            text: str,
            color: Tuple[int, int, int, int] = (255, 255, 255, 255),
            anchor: str = 'lt',
            stroke_width: int = 0,
            stroke_fill: Tuple[int, int, int, int] = (0, 0, 0, 0),
            multiline: bool = False):

        font = ImageFont.truetype(self._font, size)
        if multiline:
            self._img.multiline_text((pos_x, pos_y), str(text), color, font, anchor, stroke_width=stroke_width, stroke_fill=stroke_fill)
        else:
            self._img.text((pos_x, pos_y), str(text), color, font, anchor, stroke_width=stroke_width, stroke_fill=stroke_fill)
    
    def draw_partial_opacity(self,
            pos_x: int,
            pos_y: int,
            size: int,
            text: str,
            po: int = 2,
            color: Tuple[int, int, int, int] = (255, 255, 255, 255),
            anchor: str = 'lt',
            stroke_width: int = 0,
            stroke_fill: Tuple[int, int, int, int] = (0, 0, 0, 0)):

        font = ImageFont.truetype(self._font, size)
        self._img.text((pos_x + po, pos_y + po), str(text), (0, 0, 0, 128), font, anchor, stroke_width=stroke_width, stroke_fill=stroke_fill)
        self._img.text((pos_x, pos_y), str(text), color, font, anchor, stroke_width=stroke_width, stroke_fill=stroke_fill)

class DrawInfo:

    def __init__(self, info: dict, mode: str) -> None:
        self.icon: str = info['avatar_url']
        self.country_code: str = info['country_code']
        self.uid: int = info['id']
        self.user_status: bool = info['is_online']
        self.supporter: bool = info['is_supporter']
        self.mode: str = mode
        self.username: str = info['username']
        self.cover_url: str = info['cover_url']
        self.badges: list = info['badges']
        # self.play: dict = info['statistics']
        # self.level: dict = info['statistics']['level']
        self.current: int = info['statistics']['level']['current']
        self.progress: int = info['statistics']['level']['progress']
        self.grank: int = info['statistics']['global_rank'] if info['statistics']['global_rank'] else 0
        self.pp: float = info['statistics']['pp']
        self.r_score: int = info['statistics']['ranked_score']
        self.acc: float = round(info['statistics']['hit_accuracy'], 2)
        self.play_count: int = info['statistics']['play_count']
        self.play_time: int = info['statistics']['play_time']
        self.play_hits: int = info['statistics']['total_hits']
        self.t_score: int = info['statistics']['total_score']
        self.count: int = info['statistics']['total_hits']
        self.g_counts: dict = info['statistics']['grade_counts']
        self.gc: list = self.g_counts['ssh'], self.g_counts['ss'], self.g_counts['sh'], self.g_counts['s'], self.g_counts['a']
        self.crank: int = info['statistics']['rank']['country'] if info['statistics']['rank']['country'] else 0

    def play_time_str(self) -> str:
        sec = timedelta(seconds = self.play_time)
        d_time = datetime(1, 1, 1) + sec
        t_time = f'{sec.days}d {d_time.hour}h {d_time.minute}m {d_time.second}s'
        return t_time
    
    def score_calc(self, value: List[Union[int, float, bool]]) -> Tuple[str, Union[int, float]]:
        num = value[0] - value[1]
        if num < 0:
            if value[2]:
                op, v = '↑', num * -1
            elif value[3]:
                op, v = '↓', num * -1
            else:
                op, v = '-', num * -1
        elif num > 0:
            if value[2]:
                op, v = '↓', num
            elif value[3]:
                op, v = '↑', num
            else:
                op, v = '+', num
        else:
            op, v = '', 0
        return (op, v)

    async def draw(self):
        try:
            country = os.path.join(FILEPATH, 'flags', f'{self.country_code}.png')
            info_BG = os.path.join(FILEPATH, 'info.png')
            supporter_BG = os.path.join(FILEPATH, 'work', 'suppoter.png')
            exp_l = os.path.join(FILEPATH, 'work', 'left.png')
            exp_c = os.path.join(FILEPATH, 'work', 'center.png')
            exp_r = os.path.join(FILEPATH, 'work', 'right.png')

            info_img = Image.open(info_BG).convert('RGBA')
            user_header_img = crop_bg('Header', await get_image(self.cover_url))
            user_icon_img = Image.open((await get_image(self.icon))).convert('RGBA').resize((300, 300))
            country_img = Image.open(country).convert('RGBA').resize((80, 54))
            supporter_img = Image.open(supporter_BG).convert('RGBA').resize((54, 54))
            exp_left_img = Image.open(exp_l).convert('RGBA')
            exp_width = self.progress * 7 - 3
            exp_center_img = Image.open(exp_c).convert('RGBA').resize((exp_width, 10))
            exp_right_img = Image.open(exp_r).convert('RGBA')

            user = USER.get_user_play_info(self.uid, FGAMEMODE[self.mode])
            if user:
                n_crank, n_grank, n_pp, n_acc, n_pc, n_count = user
            else:
                n_crank, n_grank, n_pp, n_acc, n_pc, n_count = self.crank, self.grank, self.pp, self.acc, self.play_count, self.count

            self.play_score: list[tuple[Union[int, float], str]] = []
            _user = {
                'country_rank': [self.crank, n_crank, True, False],
                'global_rank': [self.grank, n_grank, True, False],
                'pp': [self.pp, n_pp, False, True],
                'acc': [self.acc, n_acc, False, False],
                'play_count': [self.play_count, n_pc, False, False],
                'count': [self.count, n_count, False, False]
            }

            for num, name in enumerate(_user):
                op, v = self.score_calc(_user[name])
                if num == 0:
                    score_str = v, f'#{_user[name][0]:,}({op}{v:,})' if v != 0 else f'#{_user[name][0]:,}'
                elif num == 1:
                    score_str = v, f'#{_user[name][0]:,}', f'{op}{v:,}'
                elif num == 2:
                    score_str = v, f'{_user[name][0]:,}', f'{op}{v:.2f}'
                elif num == 3:
                    score_str = v, f'{_user[name][0]:.2f}%({op}{v:.2f}%)' if v != 0 else f'{_user[name][0]:.2f}%'
                else:
                    score_str = v, f'{_user[name][0]:,}({op}{v:,})' if v != 0 else f'{_user[name][0]:,}'
                
                self.play_score.append(score_str)

            im = Image.new('RGBA', (1000, 1322))
            text_im = ImageDraw.Draw(im)
            trfont = DrawText(text_im, Torus_Regular)
            mrfont = DrawText(text_im, Meiryo_Regular)
            # 头图
            im.alpha_composite(user_header_img, (0, 100))
            # 底图
            im.alpha_composite(info_img)
            # 头像
            user_icon = draw_filler(user_icon_img, 25)
            im.alpha_composite(user_icon, (50, 148))
            # 地区
            im.alpha_composite(country_img, (400, 394))
            # supporter
            if self.supporter:
                im.alpha_composite(supporter_img, (400, 280))
            # 经验
            if self.progress != 0:
                im.alpha_composite(exp_left_img, (50, 646))
                im.alpha_composite(exp_center_img, (54, 646))
                im.alpha_composite(exp_right_img, (int(54 + exp_width), 646))
            # 模式
            trfont.draw(935, 50, 45, GAMEMODENAME[self.mode], anchor='rm')
            # 名字
            trfont.draw(400, 205, 50, self.username, anchor='lm')
            # 地区排名
            mrfont.draw(495, 448, 30, self.play_score[0][1], anchor='lb')
            # 等级
            trfont.draw(900, 650, 25, self.current, anchor='mm')
            # 经验百分比
            trfont.draw(750, 660, 20, f'{self.progress}%', anchor='rt')
            # 全球排名
            trfont.draw(55, 785, 35, self.play_score[1][1])
            if self.play_score[1][0] != 0:
                mrfont.draw(65, 820, 20, self.play_score[1][2])
            # pp
            trfont.draw(295, 785, 35, self.play_score[2][1])
            if self.play_score[2][0] != 0:
                mrfont.draw(305, 820, 20, self.play_score[2][2])
            # SS - A
            for gc_num, v in enumerate(self.gc):
                trfont.draw(493 + 100 * gc_num, 775, 30, f'{v:,}', anchor='mt')
            # ranked总分
            trfont.draw(935, 895, 40, f'{self.r_score:,}', anchor='rt')
            # acc
            trfont.draw(935, 965, 40, self.play_score[3][1], anchor='rt')
            # 游玩次数
            trfont.draw(935, 1035, 40, self.play_score[4][1], anchor='rt')
            # 总分
            trfont.draw(935, 1105, 40, f'{self.t_score:,}', anchor='rt')
            # 总命中
            trfont.draw(935, 1175, 40, self.play_score[5][1], anchor='rt')
            # 游玩时间
            trfont.draw(935, 1245, 40, self.play_time_str(), anchor='rt')

            return im
        except Exception as e:
            sv.logger.error(f'制图错误：{traceback.print_exc()}')
            raise DrawImageError(type(e))

class DrawScore:

    def __init__(self, project: str, info: dict, best: Optional[int] = 0, min: Optional[int] = 0,
                max: Optional[int] = 0, mods: Optional[List[str]] = []) -> None:

        self.Project = project
        self.Info = info
        self.Best = best
        self.Min = min
        self.Max = max
        self.Mods = mods

        if project == 'recent' or project == 'passrecent':
            self.RecentPerformance()
        elif project == 'bp':
            self.BestPerformance()
        elif project == 'score':
            self.MapBestPerformance()
        elif project == 'pfm':
            self.BestPerformanceList()
        elif project == 'tbp':
            self.TodayBestPerformance()
        elif project == 'tr':
            self.TodayRecentPlays()
    
    def __score__(self, scoreinfo: dict):
        self.uid: int = scoreinfo['user_id']
        self.acc: float = scoreinfo['accuracy']
        self.mods: list[str] = scoreinfo['mods']
        self.score: int = scoreinfo['score']
        self.maxcb: int = scoreinfo['max_combo']
        # self.count: dict = scoreinfo['statistics']
        self.mode: int = scoreinfo['mode_int']
        self.c50: int = scoreinfo['statistics']['count_50']
        self.c100: int = scoreinfo['statistics']['count_100']
        self.c300: int = scoreinfo['statistics']['count_300']
        self.cgeki: int = scoreinfo['statistics']['count_geki']
        self.ckatu: int = scoreinfo['statistics']['count_katu']
        self.cmiss: int = scoreinfo['statistics']['count_miss']
        self.rank: int = scoreinfo['rank']
        self.date: str = scoreinfo['created_at']
        self.pp: float = scoreinfo['pp'] if scoreinfo['pp'] else -1
        self.setid: int = scoreinfo['beatmap']['beatmapset_id']
        self.mapid: int = scoreinfo['beatmap']['id']
        self.version: str = scoreinfo['beatmap']['version']
        self.map_status: str = scoreinfo['beatmap']['status']
        # self.user: str = scoreinfo['user']
        self.icon_url: str = scoreinfo['user']['avatar_url']
        self.country_code: str = scoreinfo['user']['country_code']
        self.user_status: bool = scoreinfo['user']['is_online']
        self.supporter: bool = scoreinfo['user']['is_supporter']
        self.username: str = scoreinfo['user']['username']

    def __GetModsSum__(self, mods: List[str], max: Optional[int] = 0):
        """
        计算开启 `Mods` 的和
        """
        ModsListSum = Mods(self.Info, mods).GetModsList()
        if len(ModsListSum) > max:
            self.ModsListSum = ModsListSum[:max]
        elif self.Best:
            self.ModsListSum = []
        else:
            self.ModsListSum = ModsListSum

    def RecentPerformance(self) -> None:
        """
        指令 `recent` 和 `passrecent`
        """
        self.__score__(self.Info[0])

    def BestPerformance(self) -> None:
        """
        指令 `bp`
        """
        if self.Mods:
            self.__GetModsSum__(self.Mods, self.Best)
            if self.ModsListSum:
                self.Info = self.Info[self.ModsListSum[self.Best - 1]]
            else:
                self.Info = self.ModsListSum
                return
        else:
            self.Info = self.Info[self.Best - 1]

        self.__score__(self.Info)

    def MapBestPerformance(self) -> None:
        """
        指令 `score`
        """
        self.ModsListSum = True
        self.grank: int = self.Info['position']
        self.__score__(self.Info['score'])
    
    def BestPerformanceList(self) -> None:
        """
        指令 `pfm`
        """
        self.BPList = []
        if self.Mods:
            self.__GetModsSum__(self.Mods, self.Max)
            if self.ModsListSum:
                self.BPList = self.ModsListSum
        else:
            if self.Max > len(self.Info):
                self.BPList = f'用户的bp数量为{len(self.Info)}，超出指定范围'
            else:
                self.BPList = range(self.Min - 1, self.Max)
        
        # self.__score__(self.BPList)

    def TodayBestPerformance(self) -> None:
        """
        指令 `tbp`
        """
        self.BPList = []
        for num, v in enumerate(self.Info):
            today = datetime.now().date()
            today_stamp = mktime(strptime(str(today), '%Y-%m-%d'))
            playtime = datetime.strptime(v['created_at'].replace('+00:00', ''), '%Y-%m-%dT%H:%M:%S') + timedelta(hours=8)
            play_stamp = mktime(strptime(str(playtime), '%Y-%m-%d %H:%M:%S'))
            
            if play_stamp > today_stamp:
                self.BPList.append(num)
    
    def BestPerformanceListScore(self, bp: int) -> None:
        '''
        返回 `pfm` 和 `tbp` 成绩数据
        '''
        self.map: dict = self.Info[bp]['beatmapset']
        self.artist: str = self.map['artist_unicode'] if self.map['artist_unicode'] else self.map['artist']
        self.title: str = self.map['title_unicode'] if self.map['title_unicode'] else self.map['title']
        
        self.__score__(self.Info[bp])

    def TodayRecentPlays(self) -> None:
        '''
        返回 `tr` 成绩数据
        '''
        self.BPList = range(len(self.Info))

    async def draw_score(self, map: Beatmapset) -> Image.Image:
        try:
            if self.Project == 'bp' or self.Project == 'recent' or self.Project == 'passrecent':
                self.grank = '--'
            pp = PPCalc(self.mode, self.mapid)
            if self.mode == 0:
                _pp, ifpp, sspp, aim_pp, speed_pp, acc_pp, stars, ar, od = await pp.osu_pp(self.acc, self.maxcb, self.c300, self.c100, self.c50, self.cmiss, self.mods)
                pp = int(self.pp) if self.pp != -1 else _pp
            elif self.mode == 1:
                _pp, ifpp, stars = await pp.taiko_pp(self.acc, self.maxcb, self.c300, self.c100, self.c50, self.cmiss, self.mods)
                pp = int(self.pp) if self.pp != -1 else _pp
            elif self.mode == 2:
                _pp, ifpp, stars = await pp.catch_pp(self.acc, self.maxcb, self.c300, self.c100, self.c50, self.ckatu, self.cmiss, self.mods)
                pp = int(self.pp) if self.pp != -1 else _pp
            elif self.mode == 3:
                _pp, ifpp, stars = await pp.mania_pp(self.acc, self.maxcb, self.c300, self.c100, self.c50, self.cgeki, self.ckatu, self.cmiss, self.score, self.mods)
                pp = int(self.pp) if self.pp != -1 else _pp

            country = os.path.join(FILEPATH, 'flags', f'{self.country_code}.png')
            status = os.path.join(FILEPATH, 'work', 'on-line.png' if self.user_status else 'off-line.png')
            supporter = os.path.join(FILEPATH, 'work', 'suppoter.png')
            bg = get_mode_image(self.mode)

            if 'HD' in self.mods or 'FL' in self.mods:
                ranking = ['XH', 'SH', 'A', 'B', 'C', 'D', 'F']
            else:
                ranking = ['X', 'S', 'A', 'B', 'C', 'D', 'F']
            
            cover = await get_image(f'https://assets.ppy.sh/beatmaps/{self.setid}/covers/cover@2x.jpg')
            cover_img = ImageEnhance.Brightness(crop_bg('BG', cover).filter(ImageFilter.GaussianBlur(1))).enhance(2 / 4.0)
            bg_img = Image.open(bg).convert('RGBA')
            mode_img = stars_diff(self.mode, stars).resize((30, 30))
            stars_img = stars_diff('stars', stars).resize((23, 23))
            score_acc_img = Image.open(wedge_acc(self.acc * 100)).convert('RGBA').resize((576, 432))
            icon = Image.open(await get_image(self.icon_url)).convert('RGBA').resize((150, 150))
            icon_img = draw_filler(icon, 25)
            country_img = Image.open(country).convert('RGBA').resize((58, 39))
            status_img = Image.open(status).convert('RGBA').resize((45, 45))
            
            # 作图
            im = Image.new('RGBA', (1500, 800))
            # 字体
            text_im = ImageDraw.Draw(im)
            trfont = DrawText(text_im, Torus_Regular)
            tsfont = DrawText(text_im, Torus_SemiBold)
            msfont = DrawText(text_im, Meiryo_SemiBold)
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
            if self.mods:
                for num, s in enumerate(self.mods):
                    mods_img = Image.open(os.path.join(FILEPATH, 'mods', f'{s}.png')).convert('RGBA')
                    im.alpha_composite(mods_img, (500 + 50 * num, 240))
            # 游玩评价
            rank_ok = False
            for num, i in enumerate(ranking):
                rank_img = os.path.join(FILEPATH, 'ranking', f'ranking-{i}.png')
                rank_b = Image.open(rank_img).resize((48, 24))
                if rank_ok:
                    rank_new = Image.new('RGBA', rank_b.size, (0, 0, 0, 0))
                    rank_bg = Image.blend(rank_new, rank_b, 0.5)
                elif i != self.rank:
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
            if self.supporter:
                supporter_img = Image.open(supporter).convert('RGBA').resize((40, 40))
                im.alpha_composite(supporter_img, (300, 606))
            # 地图难度
            if self.mode == 0:
                mapdiff = [map.cs, map.hp, od, ar, stars]
            else:
                mapdiff = [map.cs, map.hp, map.od, map.ar, stars]
            for num, i in enumerate(mapdiff):
                color = (255, 204, 34, 255) if num == 4 else (255, 255, 255, 255)
                len = int(250 * i / 10) if i <= 10 else 250
                im.alpha_composite(Image.new('RGBA', (len, 8), color), (1190, 386 + 35 * num))
                tsfont.draw(1470, 386 + 35 * num, 20, i, anchor='mm')
            # 地图数据
            for num, i in enumerate([calc_songlen(map.total_len), map.bpm, map.c_circles, map.c_sliders]):
                trfont.draw(1070 + 120 * num, 325, 20, i, (255, 204, 34, 255), anchor='lm')
            # 地图状态
            tsfont.draw(1400, 264, 20, map.status.capitalize(), anchor='mm')
            # ID
            tsfont.draw(1425, 40, 27, f'Setid: {self.setid}  |  Mapid: {self.mapid}', anchor='rm')
            # 标题和曲师
            msfont.draw(75, 118, 30, f'{map.title} | by {map.artist}', anchor='lm')
            # 星数
            tsfont.draw(162, 169, 18, stars, anchor='lm')
            # 版本
            tsfont.draw(225, 169, 22, f'{map.version} | mapper by {map.mapper}', anchor='lm')
            # 评价
            vfont.draw(309, 375, 75, self.rank, anchor='mm')
            # 分数
            trfont.draw(498, 331, 75, f'{self.score:,}', anchor='lm')
            # 玩家名
            tsfont.draw(498, 396, 18, 'Played by:', anchor='lm')
            tsfont.draw(630, 396, 18, self.username, anchor='lm')
            # 游玩时间
            tsfont.draw(498, 421, 18, 'Submitted on:', anchor='lm')
            tsfont.draw(630, 421, 18, strtime(self.date), anchor='lm')
            # 全球排名
            tsfont.draw(513, 496, 24, self.grank, anchor='lm')
            # 玩家名
            tsfont.draw(230, 670, 24, self.username, anchor='lm')
            # 在线状态
            tsfont.draw(300, 732, 30, 'online' if self.user_status else 'offline', anchor='lm')
            # 游玩信息
            if self.mode == 0:
                trfont.draw(650, 625, 30, sspp, anchor='mm')
                trfont.draw(770, 625, 30, ifpp, anchor='mm')
                trfont.draw(890, 625, 30, pp, anchor='mm')
                trfont.draw(650, 720, 30, aim_pp, anchor='mm')
                trfont.draw(770, 720, 30, speed_pp, anchor='mm')
                trfont.draw(890, 720, 30, acc_pp, anchor='mm')
                trfont.draw(1087, 625, 30, f'{self.acc * 100:.2f}%', anchor='mm')
                trfont.draw(1315, 625, 30, f'{self.maxcb:,}/{map.maxcb:,}', anchor='mm')
                trfont.draw(1030, 720, 30, self.c300, anchor='mm')
                trfont.draw(1144, 720, 30, self.c100, anchor='mm')
                trfont.draw(1258, 720, 30, self.c50, anchor='mm')
                trfont.draw(1372, 720, 30, self.cmiss, anchor='mm')
            elif self.mode == 1:
                trfont.draw(1050, 625, 30, f'{self.acc * 100:.2f}%', anchor='mm')
                trfont.draw(1202, 625, 30, f'{self.maxcb:,}/{map.maxcb:,}', anchor='mm')
                trfont.draw(1352, 625, 30, f'{pp}/{ifpp}', anchor='mm')
                trfont.draw(1050, 720, 30, self.c300, anchor='mm')
                trfont.draw(1202, 720, 30, self.c100, anchor='mm')
                trfont.draw(1352, 720, 30, self.cmiss, anchor='mm')
            elif self.mode == 2:
                trfont.draw(1016, 625, 30, f'{self.acc * 100:.2f}%', anchor='mm')
                trfont.draw(1180, 625, 30, f'{self.maxcb:,}/{map.maxcb:,}', anchor='mm')
                trfont.draw(1344, 625, 30, f'{pp}/{ifpp}', anchor='mm')
                trfont.draw(995, 720, 30, self.c300, anchor='mm')
                trfont.draw(1118, 720, 30, self.c100, anchor='mm')
                trfont.draw(1242, 720, 30, self.ckatu, anchor='mm')
                trfont.draw(1365, 720, 30, self.cmiss, anchor='mm')
            else:
                trfont.draw(935, 625, 30, f'{self.acc * 100:.2f}%', anchor='mm')
                trfont.draw(1130, 625, 30, f'{self.maxcb:,}', anchor='mm')
                trfont.draw(1328, 625, 30, f'{pp}/{ifpp}', anchor='mm')
                trfont.draw(886, 720, 30, self.cgeki, anchor='mm')
                trfont.draw(984, 720, 30, self.c300, anchor='mm')
                trfont.draw(1083, 720, 30, self.ckatu, anchor='mm')
                trfont.draw(1182, 720, 30, self.c100, anchor='mm')
                trfont.draw(1280, 720, 30, self.c50, anchor='mm')
                trfont.draw(1378, 720, 30, self.cmiss, anchor='mm')
                
            
            return im
        except Exception as e:
            sv.logger.error(f'制图错误：{traceback.print_exc()}')
            raise DrawImageError(type(e))

    def draw_pfm(self, username: str, mode: str) -> Image.Image:
        try:
            bplist_len = len(self.BPList)
            bg = os.path.join(FILEPATH, 'Best Performance.png')

            bg_img = Image.open(bg).convert('RGBA')
            f_div = Image.new('RGBA', (1500, 2), (255, 255, 255, 255)).convert('RGBA')
            div = Image.new('RGBA', (1450, 2), (46, 53, 56, 255)).convert('RGBA')

            # 作图
            im = Image.new('RGBA', (1500, 180 + 82 * (bplist_len - 1)), (31, 41, 46, 255))
            # 字体
            text_im = ImageDraw.Draw(im)
            trfont = DrawText(text_im, Torus_Regular)
            tsfont = DrawText(text_im, Torus_SemiBold)
            mrfont = DrawText(text_im, Meiryo_Regular)
            # 底图
            im.alpha_composite(bg_img)
            # 分割线
            im.alpha_composite(f_div, (0, 100))
            if self.Project == 'pfm':
                uinfo = f"{username}'s | {mode.capitalize()} | BP {self.Min} - {self.Max}"
            elif self.Project == 'tbp':
                uinfo = f"{username}'s | {mode.capitalize()} | Today New BP"
            else:
                uinfo = f"{username}'s | {mode.capitalize()} | Today Recent Plays"
            tsfont.draw(1450, 50, 25, uinfo, anchor='rm')
            for num, bp in enumerate(self.BPList):
                h_num = 82 * num
                self.BestPerformanceListScore(bp)
                # mods
                if self.mods:
                    for mods_num, s_mods in enumerate(self.mods):
                        mods_bg = os.path.join(FILEPATH, 'mods', f'{s_mods}.png')
                        mods_img = Image.open(mods_bg).convert('RGBA')
                        im.alpha_composite(mods_img, (1000 + 50 * mods_num, 126 + h_num))
                    if (self.rank == 'X' or self.rank == 'S') and ('HD' in self.mods or 'FL' in self.mods):
                        self.rank += 'H'
                # BP排名
                if self.Project != 'tr':
                    mrfont.draw(20, 143 + h_num, 20, bp + 1, anchor='mm')
                # rank
                rank_img = os.path.join(FILEPATH, 'ranking', f'ranking-{self.rank}.png')
                rank_bg = Image.open(rank_img).convert('RGBA').resize((64, 32))
                im.alpha_composite(rank_bg, (45, 128 + h_num))
                # 曲名&作曲
                mrfont.draw(125, 130 + h_num, 20, f'{self.title}  |  by {self.artist}', anchor='lm')
                # 地图版本
                x = trfont.get_box(self.version, 18)
                trfont.draw(125, 158 + h_num, 18, self.version, (238, 171, 0, 255), anchor='lm')
                # 时间
                old_time = datetime.strptime(self.date.replace('+00:00', ''), '%Y-%m-%dT%H:%M:%S')
                new_time = (old_time + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
                trfont.draw(125 + x[2], 158 + h_num, 18, f'  |  {new_time}', anchor='lm')
                # acc
                tsfont.draw(1250, 130 + h_num, 22, f'{self.acc * 100:.2f}%', (238, 171, 0, 255), anchor='lm')
                # mapid
                trfont.draw(1250, 158 + h_num, 18, f'ID: {self.mapid}', anchor='lm')
                # pp
                tsfont.draw(1420, 140 + h_num, 25, int(self.pp) if self.pp != -1 else '--', (255, 102, 171, 255), anchor='rm')
                tsfont.draw(1450, 140 + h_num, 25, 'pp', (209, 148, 176, 255), anchor='rm')
                # 分割线
                im.alpha_composite(div, (25, 180 + h_num))

            return im
        except Exception as e:
            sv.logger.error(f'制图错误：{traceback.print_exc()}')
            raise DrawImageError(type(e))

def img2b64(img: Image.Image) -> str:
    bytesio = BytesIO()
    img.save(bytesio, 'PNG')
    bytes = bytesio.getvalue()
    base64_str = base64.b64encode(bytes).decode()
    return 'base64://' + base64_str

def strtime(time: str) -> str:
    old_time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%SZ')
    new_time = (old_time + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    return new_time

def calc_songlen(len: int) -> str:
    map_len = list(divmod(int(len), 60))
    map_len[1] = map_len[1] if map_len[1] >= 10 else f'0{map_len[1]}'
    music_len = f'{map_len[0]}:{map_len[1]}'
    return music_len

def osubytes(osu: bytes) -> TextIOWrapper:
    return TextIOWrapper(BytesIO(osu), 'utf-8')

def playtime(date: int) -> str:
    return strftime('%Y-%m-%d %H:%M:%S', localtime(date / 1000))

async def draw_info(id: Union[int, str], mode: str, isint: bool) -> Union[str, MessageSegment]:
    try:
        UserInfo = await osu_api('info', id, mode, isint=isint)
        if not UserInfo:
            return '未查询到该玩家'
        elif not UserInfo['statistics']['play_count']:
            return f'此玩家尚未游玩过{GAMEMODENAME[mode]}模式'
        elif isinstance(UserInfo, dict):
            data = DrawInfo(UserInfo, mode)
            im = await data.draw()
            # 输出
            base = img2b64(im)
            msg = MessageSegment.image(base)
    except DrawImageError as e:
        sv.logger.error(f'制图错误：{traceback.format_exc()}\n类型：{e.value}')
        msg = f'Error: {e.value}'
    except Exception as e:
        sv.logger.error(f'制图错误：{traceback.format_exc()}')
        msg = f'Error: {type(e)}'
    return msg

# @profile
async def draw_score(project: str, id: str, mode: str, best: int = 0, mods: list = [],
                        mapid: int = 0, isint: bool = False) -> Union[str, MessageSegment]:
    try:
        sv.logger.info(f'Start Request OsuAPI {playtime(time() * 1000)}')
        info = await osu_api(project, id, mode, mapid, mods, isint)
        if not info:
            return '未查询到游玩记录'
        elif isinstance(info, str):
            return info
        
        data = DrawScore(project, info, best, mods=mods)
        if mods and not data.ModsListSum:
            return f'未找到开启 {"|".join(mods)} Mods的第{best}个成绩'

        mapJson = await osu_api('map', mapid=data.mapid)
        sv.logger.info(f'Ending Request OsuAPI {playtime(time() * 1000)}')

        map = Beatmapset(mapJson)
        im = await data.draw_score(map)
        
        base = img2b64(im)
        msg = MessageSegment.image(base)
    except Exception as e:
        sv.logger.error(f'制图错误：{traceback.print_exc()}')
        msg = f'Error: {type(e)}'
    return msg

async def best_pfm(project: str, id: Union[str, int], mode: str, min: int = 0, max: int = 0, mods: list = [], isint: bool = False) -> Union[str, MessageSegment]:  
    try:
        BPInfo = await osu_api(project, id, mode, isint=isint)
        if not BPInfo:
            return '未查询到游玩记录'
        if isinstance(BPInfo, str):
            return BPInfo
        info = DrawScore(project, BPInfo, min=min, max=max, mods=mods)
        username = BPInfo[0]['user']['username']
        if project == 'pfm':
            if isinstance(info.BPList, str):
                return info.BPList
            if mods and not info.ModsListSum:
                return f'未找到开启 {"|".join(mods)} Mods的成绩'
        elif project == 'tbp':
            if not info.BPList:
                return f'今天没有新增的BP成绩'

        im = info.draw_pfm(username, mode)

        base = img2b64(im)
        msg = MessageSegment.image(base)
    except Exception as e:
        sv.logger.error(f'制图错误：{traceback.print_exc()}')
        msg = f'Error: {type(e)}'
    return msg

async def map_info(mapid: int, mods: list) -> Union[str, MessageSegment]: 
    try:
        info = await osu_api('map', mapid=mapid)
        if not info:
            return '未查询到该地图信息'
        if isinstance(info, str): 
            return info
        mapinfo = Beatmapset(info)
        diffinfo = calc_songlen(mapinfo.total_len), mapinfo.bpm, mapinfo.c_circles, mapinfo.c_sliders
        # pp
        if mapinfo.mode == 0:
            pp, stars, ar, od = await PPCalc(mapinfo.mode, mapid).if_pp(mods=mods)
        else:
            pp, stars = await PPCalc(mapinfo.mode, mapid).if_pp(mods=mods)
        # 计算时间
        if mapinfo.ranked_date:
            old_time = datetime.strptime(mapinfo.ranked_date.replace('+00:00', ''), '%Y-%m-%dT%H:%M:%S')
            new_time = (old_time + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
        else:
            new_time = '??-??-?? ??:??:??'

        bg = os.path.join(FILEPATH, 'beatmapinfo.png')
        cover = await get_image(mapinfo.cover)
        user_icon = await get_image(f'https://a.ppy.sh/{mapinfo.uid}')

        bg_img = Image.open(bg).convert('RGBA')
        cover_img = ImageEnhance.Brightness(crop_bg('MAPBG', cover)).enhance(2 / 4.0)
        mode_img = stars_diff(mapinfo.mode, stars).resize((50, 50))
        icon = Image.open(user_icon).convert('RGBA').resize((100, 100))
        icon_img = draw_filler(icon, 10)
        
        # BG做地图
        im = Image.new('RGBA', (1200, 600))
        im.alpha_composite(cover_img)
        # 字体
        text_im = ImageDraw.Draw(im)
        trfont = DrawText(text_im, Torus_Regular)
        tsfont = DrawText(text_im, Torus_SemiBold)
        msfont = DrawText(text_im, Meiryo_SemiBold)
        # 获取地图info
        im.alpha_composite(bg_img)
        # 模式
        im.alpha_composite(mode_img, (50, 100))
        # cs - diff
        if mapinfo.mode == 0:
            mapdiff = [mapinfo.cs, mapinfo.hp, od, ar, stars]
        else:
            mapdiff = [mapinfo.cs, mapinfo.hp, mapinfo.od, mapinfo.ar, stars]
        for num, i in enumerate(mapdiff):
            color = (255, 255, 255, 255)
            if num == 4:
                color = (255, 204, 34, 255)
            difflen = int(250 * i / 10) if i <= 10 else 250
            diff_len = Image.new('RGBA', (difflen, 8), color)
            im.alpha_composite(diff_len, (890, 426 + 35 * num))
            tsfont.draw(1170, 426 + 35 * num, 20, i, anchor='mm')
        # mapper
        im.alpha_composite(icon_img, (50, 400))
        # mapid
        tsfont.draw(800, 40, 22, f'Setid: {mapinfo.setid}  |  Mapid: {mapid}', anchor='lm')
        # 版本
        tsfont.draw(120, 125, 25, mapinfo.version, anchor='lm')
        # 曲名
        msfont.draw(50, 170, 30, mapinfo.title)
        # 曲师
        msfont.draw(50, 210, 25, f'by {mapinfo.artist}')
        # 来源
        msfont.draw(50, 260, 25, f'Source:{mapinfo.source}')
        # mapper
        tsfont.draw(160, 400, 20, 'mapper by:')
        tsfont.draw(160, 425, 20, mapinfo.mapper)
        # ranked时间
        tsfont.draw(160, 460, 20, 'ranked by:')
        tsfont.draw(160, 485, 20, new_time)
        # 状态
        tsfont.draw(1100, 304, 20, mapinfo.status.capitalize(), anchor='mm')
        # 时长 - 滑条
        for num, i in enumerate(diffinfo):
            trfont.draw(770 + 120 * num, 365, 20, i, (255, 204, 34, 255), anchor='lm')
        # maxcb
        tsfont.draw(50, 570, 20, f'Max Combo: {mapinfo.maxcb}', anchor='lm')
        # pp
        tsfont.draw(320, 570, 20, f'SS PP: {pp}', anchor='lm')
        # 输出
        base = img2b64(im)
        msg = MessageSegment.image(base)
    except Exception as e:
        sv.logger.error(f'制图错误：{traceback.print_exc()}')
        msg = f'Error: {type(e)}'
    return msg

async def bmap_info(mapid: int, op: bool=False) -> Union[str, MessageSegment]:
    if op:
        info = await osu_api('map', mapid=mapid)
        if not info:
            return '未查询到地图'
        elif isinstance(info, str):
            return info
        mapid = info['beatmapset_id']
    info = await SayoApi(mapid)
    if info['status'] == -1:
        return '未查询到地图'
    elif isinstance(info, str):
        return info
    try:
        songinfo = SayoInfo(info['data'])
        songinfo.map(info['data'])
        cover = await get_image(f'https://assets.ppy.sh/beatmaps/{mapid}/covers/cover@2x.jpg')
        # 作图
        if len(songinfo.gmap) > 20:
            im_h = 400 + 102 * 20
        else:
            im_h = 400 + 102 * (len(songinfo.gmap) - 1)
        im = Image.new('RGBA', (1200, im_h), (31, 41, 46, 255))
        # 字体
        text_im = ImageDraw.Draw(im)
        tsfont = DrawText(text_im, Torus_SemiBold)
        msfont = DrawText(text_im, Meiryo_SemiBold)
        # 背景
        cover_crop = crop_bg('MP', cover)
        cover_gb = cover_crop.filter(ImageFilter.GaussianBlur(1))
        cover_img = ImageEnhance.Brightness(cover_gb).enhance(2 / 4.0)
        # 分割线
        div = Image.new('RGBA', (1150, 2), (46, 53, 56, 255)).convert('RGBA')
        im.alpha_composite(cover_img, (0, 0))
        # 曲名
        msfont.draw(25, 40, 38, songinfo.title)
        # 曲师
        msfont.draw(25, 75, 20, f'by {songinfo.artist}')
        # mapper
        tsfont.draw(25, 110, 20, f'mapper by {songinfo.mapper}')
        # rank时间
        if songinfo.apptime == -1:
            songinfo.apptime = '??-??-?? ??:??:??'
        else:
            datearray = datetime.utcfromtimestamp(songinfo.apptime)
            songinfo.apptime = (datearray + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
        tsfont.draw(25, 145, 20, f'Approved Time: {songinfo.apptime}')
        # 来源
        msfont.draw(25, 180, 20, f'Source: {songinfo.source}')
        # bpm
        tsfont.draw(1150, 110, 20, f'BPM: {songinfo.bpm}', anchor='rt')
        # 曲长
        music_len = calc_songlen(songinfo.songlen)
        tsfont.draw(1150, 145, 20, f'lenght: {music_len}', anchor='rt')
        # Setid
        tsfont.draw(1150, 20, 20, f'Setid: {mapid}', anchor='rt')
        gmap = sorted(songinfo.gmap, key=lambda k: k['star'], reverse=False)
        for num, cmap in enumerate(gmap):
            if num < 20:
                h_num = 102 * num
                songinfo.mapinfo(cmap)
                # 难度
                mode_bg = stars_diff(songinfo.mode, songinfo.star)
                mode_img = mode_bg.resize((20, 20))
                im.alpha_composite(mode_img, (20, 320 + h_num))
                # 星星
                stars_bg = stars_diff('stars', songinfo.star)
                stars_img = stars_bg.resize((20, 20))
                im.alpha_composite(stars_img, (50, 320 + h_num))
                # diff
                bar_bg = os.path.join(FILEPATH, 'work', 'bmap.png')
                bar_img = Image.open(bar_bg).convert('RGBA')
                im.alpha_composite(bar_img, (10, 365 + h_num))
                gc = ['CS', 'HP', 'OD', 'AR']
                for num, i in enumerate(songinfo.diff):
                    diff_len = int(200 * i / 10) if i <= 10 else 200
                    diff_bg = Image.new('RGBA', (diff_len, 12), (255, 255, 255, 255))
                    im.alpha_composite(diff_bg, (50 + 300 * num, 365 + h_num))
                    tsfont.draw(20 + 300 * num, 369 + h_num, 20, gc[num], anchor='lm')
                    tsfont.draw(265 + 300 * num, 369 + h_num, 20, i, (255, 204, 34, 255), anchor='lm')
                    if num != 3:
                        tsfont.draw(300 + 300 * num, 369 + h_num, 20, '|', anchor='lm')
                # 难度
                tsfont.draw(80, 328 + h_num, 20, songinfo.star, anchor='lm')
                # version
                tsfont.draw(125, 328 + h_num, 20, f' |  {songinfo.version}', anchor='lm')
                # mapid
                tsfont.draw(1150, 328 + h_num, 20, f'Mapid: {songinfo.bid}', anchor='rm')
                # maxcb
                tsfont.draw(700, 328 + h_num, 20, f'Max Combo: {songinfo.maxcb}', anchor='lm')
                # 分割线
                im.alpha_composite(div, (25, 400 + h_num))
            else:
                plusnum = f'+ {num - 19}'
        if num >= 20:
            tsfont.draw(600, 350 + 102 * 20, 50, plusnum, anchor='mm')

        base = img2b64(im)
        msg = MessageSegment.image(base)
    except Exception as e:
        sv.logger.error(f'制图错误：{traceback.print_exc()}')
        msg = f'Error: {type(e)}'
    return msg

async def bindinfo(project: str, id: str, qid: int) -> str:
    info = await osu_api(project, id)
    if not info:
        return '未查询到该玩家'
    elif isinstance(info, str):
        return info
    uid = info['id']
    name = info['username']
    mode = FGAMEMODE[info['playmode']]
    USER.insert_user_info(qid, uid, name, mode)
    await user(uid)
    msg = f'用户 {name} 已成功绑定QQ {qid}'
    return msg

async def get_map_bg(mapid: Union[str, int]) -> MessageSegment:
    info = await osu_api('map', mapid=mapid)
    if not info:
        return '未查询到该地图'
    elif isinstance(info, str):
        return info
    setid: int = info['beatmapset_id']
    dirpath = await MapDownload(setid)
    osu = await osu_file_download(mapid)
    path = await re_map(osubytes(osu))
    msg = MessageSegment.image(f'''file:///{os.path.join(dirpath, path)}''')
    return msg

async def user(id: int, update: bool = False):
    for mode in range(0, 4):
        # if not update:
        #     new = USER.get_user_play_info(id, mode)
        userinfo = await osu_api('update', id, GAMEMODE[mode], isint=True)
        if userinfo['statistics']['play_count'] != 0:
            info = DrawInfo(userinfo, str(mode))
            if update:
                USER.update_user_play_info(id, info.crank, info.grank, info.pp, round(info.acc, 2), info.play_count, info.play_hits, mode)
            else:
                USER.insert_user_play_info(id, info.crank, info.grank, info.pp, round(info.acc, 2), info.play_count, info.play_hits, mode)
        else:
            if update:
                USER.update_user_play_info(id, 0, 0, 0, 0, 0, 0, mode)
            else:
                USER.insert_user_play_info(id, 0, 0, 0, 0, 0, 0, mode)
        sv.logger.info(f'玩家:[{userinfo["username"]}] {GAMEMODE[mode]}模式 个人信息更新完毕')