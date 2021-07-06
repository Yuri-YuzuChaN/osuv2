from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from datetime import datetime, timedelta
import hoshino, os, asyncio, io
import matplotlib.pyplot as plt

from .api import OsuApi, ChimuApi, SayoApi
from .file import *
from .pp import *
from .mods import *
from .sql import osusql
from .http import FILEHTTP
from .data import ChumiInfo, SayoInfo, UserInfo, ScoreInfo, Beatmapset

esql = osusql()

log = hoshino.new_logger('osuv2_draw')

Torus_Regular = os.path.join(osufile, 'fonts', 'Torus Regular.otf')
Torus_SemiBold = os.path.join(osufile, 'fonts', 'Torus SemiBold.otf')
Meiryo_Regular = os.path.join(osufile, 'fonts', 'Meiryo Regular.ttf')
Meiryo_SemiBold = os.path.join(osufile, 'fonts', 'Meiryo SemiBold.ttf')
Venera = os.path.join(osufile, 'fonts', 'Venera.otf')

GM = {0 : 'osu', 1 : 'taiko', 2 : 'fruits', 3 : 'mania'}
GMN = {'osu' : 'Std', 'taiko' : 'Taiko', 'fruits' : 'Ctb', 'mania' : 'Mania'}
FGM = {'osu' : 0 , 'taiko' : 1 , 'fruits' : 2 , 'mania' : 3}
sayo = [1, 2, 4, 8, 8, 16]
chimu = [1, 3, 4, 0, -1, -2]
        
class datatext:
    #L=X轴，T=Y轴，size=字体大小，fontpath=字体文件，
    def __init__(self, L, T, size, text, path, anchor = 'lt'):
        self.L = L
        self.T = T
        self.text = str(text)
        self.path = path
        self.font = ImageFont.truetype(self.path, size)
        self.anchor = anchor

def write_text(image, font, text='text', pos=(0, 0), color=(255, 255, 255, 255), anchor='lt'):
    rgba_image = image.convert('RGBA')
    text_overlay = Image.new('RGBA', rgba_image.size, (255, 255, 255, 0))
    image_draw = ImageDraw.Draw(text_overlay)
    image_draw.text(pos, text, font=font, fill=color, anchor=anchor)
    return Image.alpha_composite(rgba_image, text_overlay)

def draw_text(image, class_text: datatext, color=(255, 255, 255, 255)):
    font = class_text.font
    text = class_text.text
    anchor = class_text.anchor
    return write_text(image, font, text, (class_text.L, class_text.T), color, anchor)

def draw_fillet(img, radii):
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

def info_calc(n1, n2, rank=False, pp=False):
    num = n1 - n2
    if num < 0:
        if rank:
            op, value = '↑', num * -1
        elif pp:
            op, value = '↓', num * -1
        else:
            op, value = '-', num * -1
    elif num > 0:
        if rank:
            op, value = '↓', num
        elif pp:
            op, value = '↑', num
        else:
            op, value = '+', num
    else:
        op, value = '', 0
    return op, value

def wedge_acc(acc):
    size = [acc, 100-acc]
    insize = [60, 20, 7, 7, 5, 1]
    insizecolor = ['#ff5858', '#ea7948', '#d99d03', '#72c904', '#0096a2', '#be0089']
    fig, ax = plt.subplots()
    patches, texts = ax.pie(size, radius=1.1, startangle=90, counterclock=False, pctdistance=0.9, wedgeprops=dict(width=0.27))
    ax.pie(insize, radius=0.8, colors=insizecolor, startangle=90, counterclock=False, pctdistance=0.9, wedgeprops=dict(width=0.05))
    patches[1].set_alpha(0)
    img = io.BytesIO()
    plt.savefig(img, transparent=True)
    return img

def crop_bg(size, path):
    bg = Image.open(path).convert('RGBA')
    bg_w, bg_h = bg.size[0], bg.size[1]
    if size == 'BG':
        fix_w = 1500
        fix_h = 360
    elif size == 'H':
        fix_w = 540
        fix_h = 180
    elif size == 'HI':
        fix_w = 1000
        fix_h = 400
    elif size == 'MP':
        fix_w = 1200
        fix_h = 300
    elif size == 'MB':
        fix_w = 1200
        fix_h = 600
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
        return bg

def stars_diff(stars):
    diff = ''
    if 0 <= stars < 2.0:
        diff = 'easy'
    elif 2.0 <= stars < 2.7:
        diff = 'normal'
    elif 2.7 <= stars < 4.0:
        diff = 'hard'
    elif 4.0 <= stars < 5.3:
        diff = 'insane'
    elif 5.3 <= stars < 6.5:
        diff = 'expert'
    elif 6.5 <= stars :
        diff = 'expertplus'
    return diff

def calc_songlen(len):
    map_len = list(divmod(int(len), 60))
    map_len[1] = map_len[1] if map_len[1] >= 10 else f'0{map_len[1]}'
    music_len = f'{map_len[0]}:{map_len[1]}'
    return music_len

async def draw_info(id, mode):
    try:
        info_json = await OsuApi('info', id, mode)
        if not info_json:
            return '未查询到该玩家'
        info = UserInfo(info_json)
        if info.play_count == 0:
            return f'此玩家尚未游玩过{GMN[mode]}模式'
        #对比
        result = esql.get_all_newinfo(info.uid, FGM[mode])
        if result:
            for i in result:
                n_crank = i[2]
                n_grank = i[3]
                n_pp = i[4]
                n_acc = i[5]
                n_pc = i[6]
                n_count = i[7]
        else:
            n_crank, n_grank, n_pp, n_acc, n_pc, n_count = info.crank, info.grank, info.pp, info.acc, info.play_count, info.count
        #新建
        im = Image.new('RGBA', (1000, 1322))
        #获取头图，头像，地区，状态，supporter
        user_header = await get_projectimg(info.cover_url, 'header', info.uid)
        user_icon = await get_projectimg(info.icon, 'icon', info.uid)
        country = os.path.join(osufile, 'flags', f'{info.country_code}.png')
        supporter = os.path.join(osufile, 'work', 'suppoter.png')
        exp_l = os.path.join(osufile, 'work', 'left.png')
        exp_c = os.path.join(osufile, 'work', 'center.png')
        exp_r = os.path.join(osufile, 'work', 'right.png')
        #头图
        header_img = crop_bg('HI', user_header)
        im.alpha_composite(header_img, (0, 100))
        #底图
        info_bg = os.path.join(osufile, 'info.png')
        info_img = Image.open(info_bg).convert('RGBA')
        im.alpha_composite(info_img)
        #头像
        icon_bg = Image.open(user_icon).convert('RGBA').resize((300, 300))
        icon_img = draw_fillet(icon_bg, 25)
        im.alpha_composite(icon_img, (50, 148))
        #奖牌
        if info.badges:
            badges_num = len(info.badges)
            for num, _ in enumerate(info.badges):
                if badges_num <= 9:
                    L = 50 + 100 * num
                    T = 530
                elif num < 9:
                    L = 50 + 100 * num
                    T = 506
                else:
                    L = 50 + 100 * (num - 9)
                    T = 554
                badges_path = await get_projectimg(_['image_url'])
                badges_img = Image.open(badges_path).convert('RGBA').resize((86, 40))
                im.alpha_composite(badges_img, (L, T))
        else:
            w_badges = datatext(500, 545, 35, "You don't have a badge", Torus_Regular, anchor='mm')
            im = draw_text(im, w_badges)
        #地区
        country_bg = Image.open(country).convert('RGBA').resize((80, 54))
        im.alpha_composite(country_bg, (400, 394))
        #supporter
        if info.supporter:
            supporter_bg = Image.open(supporter).convert('RGBA').resize((54, 54))
            im.alpha_composite(supporter_bg, (400, 280))
        #经验
        if info.progress != 0:
            exp_left_bg = Image.open(exp_l).convert('RGBA')
            im.alpha_composite(exp_left_bg, (50, 646))
            exp_width = info.progress * 7 - 3
            exp_center_bg = Image.open(exp_c).convert('RGBA').resize((exp_width ,10))
            im.alpha_composite(exp_center_bg, (54, 646))
            exp_right_bg = Image.open(exp_r).convert('RGBA')
            im.alpha_composite(exp_right_bg, (int(54 + exp_width), 646))
        #模式
        w_mode = datatext(935, 50, 45, GMN[mode], Torus_Regular, anchor='rm')
        im = draw_text(im, w_mode)
        #玩家名
        w_name = datatext(400, 205, 50, info.username, Torus_Regular, anchor='lm')
        im = draw_text(im, w_name)
        #地区排名
        op, value = info_calc(info.crank, n_crank, rank=True)
        t_crank = f'#{info.crank:,}({op}{value:,})' if value != 0 else f'#{info.crank:,}'
        w_crank = datatext(495, 448, 30, t_crank, Meiryo_Regular, anchor='lb')
        im = draw_text(im, w_crank)
        #等级
        w_current = datatext(900, 650, 25, info.current, Torus_Regular, anchor='mm')
        im = draw_text(im, w_current)
        #经验百分比
        w_progress = datatext(750, 660, 20, f'{info.progress}%', Torus_Regular, anchor='rt')
        im = draw_text(im, w_progress)
        #全球排名
        w_grank = datatext(55, 785, 35, f'#{info.grank:,}', Torus_Regular)
        im = draw_text(im, w_grank)
        op, value = info_calc(info.grank, n_grank, rank=True)
        if value != 0:
            w_n_grank = datatext(65, 820, 20, f'{op}{value:,}', Meiryo_Regular)
            im = draw_text(im, w_n_grank)
        #pp
        w_pp = datatext(295, 785, 35, f'{info.pp:,}', Torus_Regular)
        im = draw_text(im, w_pp)
        op, value = info_calc(info.pp, n_pp, pp=True)
        if value != 0:
            w_n_pc = datatext(305, 820, 20, f'{op}{value:.2f}', Meiryo_Regular)
            im = draw_text(im, w_n_pc)
        #SS - A
        # gc_x = 493
        for gc_num, i in enumerate(info.gc):
            w_ss_a = datatext(493 + 100 * gc_num, 775, 30, f'{i:,}', Torus_Regular, anchor='mt')
            im = draw_text(im, w_ss_a)
            # gc_x+=100
        #rank分
        w_r_score = datatext(935, 895, 40, f'{info.r_score:,}', Torus_Regular, anchor='rt')
        im = draw_text(im, w_r_score)
        #acc
        op, value = info_calc(info.acc, n_acc)
        t_acc = f'{info.acc:.2f}%({op}{value:.2f}%)' if value != 0 else f'{info.acc:.2f}%'
        w_acc = datatext(935, 965, 40, t_acc, Torus_Regular, anchor='rt')
        im = draw_text(im, w_acc)
        #游玩次数
        op, value = info_calc(info.play_count, n_pc)
        t_pc = f'{info.play_count:,}({op}{value:,})' if value != 0 else f'{info.play_count:,}'
        w_pc = datatext(935, 1035, 40, t_pc, Torus_Regular, anchor='rt')
        im = draw_text(im, w_pc)
        #总分
        w_t_score = datatext(935, 1105, 40, f'{info.t_score:,}', Torus_Regular, anchor='rt')
        im = draw_text(im, w_t_score)
        #总命中
        op, value = info_calc(info.count, n_count)
        t_count = f'{info.count:,}({op}{value:,})' if value != 0 else f'{info.count:,}'
        w_conut = datatext(935, 1175, 40, t_count, Torus_Regular, anchor='rt')
        im = draw_text(im, w_conut) 
        #游玩时间
        sec = timedelta(seconds = info.play_time)
        d_time = datetime(1, 1, 1) + sec
        t_time = "%dd %dh %dm %ds" % (sec.days, d_time.hour, d_time.minute, d_time.second)
        w_name = datatext(935, 1245, 40, t_time, Torus_Regular, anchor='rt')
        im = draw_text(im, w_name)
        #输出
        info_outputimage = os.path.join(osufile, 'output', f'info_{info.uid}.png')
        im.save(info_outputimage)
        msg = f'[CQ:image,file=file:///{info_outputimage}]'
    except Exception as e:
        log.error(f'制图错误：{e}')
        return f'Error: {type(e)}'
    return msg

async def draw_score(project: str, 
                    id: str, 
                    mode: str, 
                    bp: int = 0, 
                    mods: list = [], 
                    mapid: int = 0):
    try:
        scoreJson = await OsuApi(project, id, mode, mapid)
        if not scoreJson:
            return '未查询到最近游玩的记录'
        elif isinstance(scoreJson, str):
            return scoreJson
        info = ScoreInfo(scoreJson)
        if project == 'recent':
            info.RecentScore()
        elif project == 'bp':
            info.BPScore(bp, mods)
            if mods:
                if not info.modslist:
                    return '未在bp上查询到开启该mod的成绩'
        elif project == 'score':
            info.MapScore()
        else:
            raise 'Project Error'

        mapJson = await OsuApi('map', mapid=info.mapid)
        mapinfo = Beatmapset(mapJson)
        if project == 'bp' or project == 'recent':
            header = await OsuApi('info', id)
            info.headericon = header['cover_url']
            info.grank = '--'
        #下载地图
        dirpath = await MapDownload(info.setid)
        #获取文件
        version_osu = get_osufile(dirpath, info.mapid, mapinfo.version)
        #pp
        setmods = modsnum(info.mods) if info.mods else 0
        if info.mode == 0:
            _pp, aim_pp, speed_pp, acc_pp = calc_pp(version_osu, setmods, info.maxcb, info.c50, info.c100, info.c300, info.cmiss)
            pp = int(info.pp) if info.pp != -1 else _pp
            ifpp = calc_if(version_osu, setmods, info.c50, info.c100, mapinfo.maxcb)
        elif info.mode == 3:
            _pp = calc_mania_pp(version_osu, setmods, info.score)
            pp = int(info.pp) if info.pp != -1 else _pp
            ifpp = calc_mania_pp(version_osu, setmods, 1000000)
        elif project == 'recent' and info.mode != 0:
            _pp, aim_pp, speed_pp, acc_pp = '--', '--', '--', '--'
        else:
            _pp, aim_pp, speed_pp, acc_pp = int(info.pp), '--', '--', '--'
        #新建图片
        im = Image.new('RGBA', (1500, 800))
        #获取cover并裁剪，高斯，降低亮度
        cover = get_picmusic('pic', version_osu)
        cover_path = os.path.join(dirpath, cover)
        cover_crop = crop_bg('BG', cover_path)
        cover_gb = cover_crop.filter(ImageFilter.GaussianBlur(1))
        cover_img = ImageEnhance.Brightness(cover_gb).enhance(2 / 4.0)
        im.alpha_composite(cover_img, (0, 200))
        #获取成绩背景做底图
        BG = get_modeimage(info.mode)
        recent_bg = Image.open(BG).convert('RGBA')
        im.alpha_composite(recent_bg)
        #模式
        diff_name = stars_diff(mapinfo.diff)
        mode_bg = get_modeimage(info.mode, diff_name)
        mode_img = Image.open(mode_bg).convert('RGBA').resize((30, 30))
        im.alpha_composite(mode_img, (75, 154))
        #难度星星
        stars_bg = os.path.join(osufile, 'work', f'stars_{stars_diff(mapinfo.diff)}.png')
        stars_img = Image.open(stars_bg).convert('RGBA').resize((23, 23))
        im.alpha_composite(stars_img, (134, 158))
        #mods
        if info.mods:
            for mods_num, s_mods in enumerate(info.mods):
                mods_bg = os.path.join(osufile, 'mods', f'{s_mods}.png')
                mods_img = Image.open(mods_bg).convert('RGBA')
                im.alpha_composite(mods_img, (500 + 50 * mods_num , 240))
            ranking = ['XH', 'SH', 'A', 'B', 'C', 'D', 'F']
            if info.rank == 'X' or info.rank == 'S':
                info.rank = info.rank + 'H'
        else:
            ranking = ['X', 'S', 'A', 'B', 'C', 'D', 'F']
        #成绩S-F
        rank_ok = False
        for rank_num, i in enumerate(ranking):
            rank_img = os.path.join(osufile, 'ranking', f'ranking-{i}.png')
            if rank_ok:
                rank_b = Image.open(rank_img).convert('RGBA').resize((48, 24))
                rank_new = Image.new('RGBA', rank_b.size, (0,0,0,0))
                rank_bg = Image.blend(rank_new, rank_b, 0.5)
            elif i != info.rank:
                rank_b = Image.open(rank_img).convert('RGBA').resize((48, 24))
                rank_new = Image.new('RGBA', rank_b.size, (0,0,0,0))
                rank_bg = Image.blend(rank_new, rank_b, 0.2)
            else:
                rank_bg = Image.open(rank_img).convert('RGBA').resize((48, 24))
                rank_ok = True
                if info.mods:
                    if info.rank == 'XH' or info.rank == 'SH':
                        info.rank = info.rank[:-1]
            im.alpha_composite(rank_bg, (75, 243 + 39 * rank_num))
            # rank_num += 26
        #成绩+acc
        score_acc = wedge_acc(info.acc * 100)
        score_acc_bg = Image.open(score_acc).convert('RGBA').resize((576, 432))
        im.alpha_composite(score_acc_bg, (15, 153))
        #获取头图，头像，地区，状态，support
        user_headericon = await get_projectimg(info.headericon, 'header', info.uid)
        user_icon = await get_projectimg(info.icon_url, 'icon', info.uid)
        #头图
        headericon_crop = crop_bg('H', user_headericon)
        headericon_gb = headericon_crop.filter(ImageFilter.GaussianBlur(1))
        headericon_img = ImageEnhance.Brightness(headericon_gb).enhance(2 / 4.0)
        headericon_d = draw_fillet(headericon_img, 15)
        im.alpha_composite(headericon_d, (50, 591))
        #头像
        icon_bg = Image.open(user_icon).convert('RGBA').resize((90, 90))
        icon_img = draw_fillet(icon_bg, 15)
        im.alpha_composite(icon_img, (90, 606))
        #地区
        country = os.path.join(osufile, 'flags', f'{info.country_code}.png')
        country_bg = Image.open(country).convert('RGBA').resize((58, 39))
        im.alpha_composite(country_bg, (195, 606))
        #在线状态
        status = os.path.join(osufile, 'work', 'on-line.png' if info.user_status else 'off-line.png')
        status_bg = Image.open(status).convert('RGBA').resize((45, 45))
        im.alpha_composite(status_bg, (114, 712))
        #supporter
        if info.supporter:
            supporter = os.path.join(osufile, 'work', 'suppoter.png')
            supporter_bg = Image.open(supporter).convert('RGBA').resize((40, 40))
            im.alpha_composite(supporter_bg, (267, 606))
        #cs, ar, od, hp, stardiff
        for num, i in enumerate(mapinfo.mapdiff):
            color = (255, 255, 255, 255)
            if num == 4:
                color = (255, 204, 34, 255)
            difflen = int(250 * i / 10) if i <= 10 else 250
            diff_len = Image.new('RGBA', (difflen, 8), color)
            im.alpha_composite(diff_len, (1190, 386 + 35 * num))
            w_diff = datatext(1470, 386 + 35 * num, 20, f'{i:.1f}', Torus_SemiBold, anchor='mm')
            im = draw_text(im, w_diff)
        # 时长 - 滑条
        diffinfo = calc_songlen(mapinfo.total_len), mapinfo.bpm, mapinfo.c_circles, mapinfo.c_sliders
        for num, i in enumerate(diffinfo):
            w_info = datatext(1070 + 120 * num, 325, 20, i, Torus_Regular, anchor='lm')
            im = draw_text(im, w_info, (255, 204, 34, 255))
        #状态
        w_status = datatext(1400, 264, 20, mapinfo.status.capitalize(), Torus_SemiBold, anchor='mm')
        im = draw_text(im, w_status)
        #mapid
        w_mapid = datatext(1425, 40, 27, f'Setid: {info.setid}  |  Mapid: {info.mapid}', Torus_SemiBold, anchor='rm')
        im = draw_text(im, w_mapid)
        #曲名
        w_title = datatext(75, 118, 30, f'{mapinfo.title} | by {mapinfo.artist}', Meiryo_SemiBold, anchor='lm')
        im = draw_text(im, w_title)
        #星级
        w_diff = datatext(162, 169, 18, mapinfo.diff, Torus_SemiBold, anchor='lm')
        im = draw_text(im, w_diff)
        #谱面版本，mapper
        w_version = datatext(225, 169, 22, f'{mapinfo.version} | mapper by {mapinfo.mapper}', Torus_SemiBold, anchor='lm')
        im = draw_text(im, w_version)
        #评价
        w_rank = datatext(309, 375, 75, info.rank, Venera, anchor='mm')
        im = draw_text(im, w_rank)
        #分数
        w_score = datatext(498, 331, 75, f'{info.score:,}', Torus_Regular, anchor='lm')
        im = draw_text(im, w_score)
        #玩家
        w_played = datatext(498, 396, 18, 'Played by:', Torus_SemiBold, anchor='lm')
        im = draw_text(im, w_played)
        w_username = datatext(630, 396, 18, info.username, Torus_SemiBold, anchor='lm')
        im = draw_text(im, w_username)
        #时间
        w_date = datatext(498, 421, 18, 'Submitted on:', Torus_SemiBold, anchor='lm')
        im = draw_text(im, w_date)
        old_time = datetime.strptime(info.date.replace('+00:00', ''), '%Y-%m-%dT%H:%M:%S')
        new_time = (old_time + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
        w_time = datatext(630, 421, 18, new_time, Torus_SemiBold, anchor='lm')
        im = draw_text(im, w_time)
        #全球排名
        w_grank = datatext(513, 496, 24, info.grank, Torus_SemiBold, anchor='lm')
        im = draw_text(im, w_grank)
        #左下玩家名
        w_l_username = datatext(195, 670, 24, info.username, Torus_SemiBold, anchor='lm')
        im = draw_text(im, w_l_username)
        #在线，离线
        w_line = datatext(195, 732, 30, 'online' if info.user_status else 'offline', Torus_SemiBold, anchor='lm')
        im = draw_text(im, w_line)
        #acc,cb,pp,300,100,50,miss
        if info.mode == 0:
            w_acc = datatext(1050, 625, 30, f'{info.acc * 100:.2f}%', Torus_Regular, anchor='mm')
            w_maxcb = datatext(1202, 625, 30, f'{info.maxcb:,}/{mapinfo.maxcb}', Torus_Regular, anchor='mm')
            w_pp = datatext(1352, 625, 30, f'{pp}/{ifpp}', Torus_Regular, anchor='mm')
            w_300 = datatext(1030, 720, 30, info.c300, Torus_Regular, anchor='mm')
            w_100 = datatext(1144, 720, 30, info.c100, Torus_Regular, anchor='mm')
            w_50 = datatext(1258, 720, 30, info.c50, Torus_Regular, anchor='mm')
            im = draw_text(im, w_50)
            w_miss = datatext(1372, 720, 30, info.cmiss, Torus_Regular, anchor='mm')
        elif info.mode == 1:
            w_acc = datatext(1050, 625, 30, f'{info.acc * 100:.2f}%', Torus_Regular, anchor='mm')
            w_maxcb = datatext(1202, 625, 30, f'{info.maxcb:,}/{mapinfo.maxcb}', Torus_Regular, anchor='mm')
            w_pp = datatext(1352, 625, 30, pp, Torus_Regular, anchor='mm')
            w_300 = datatext(1050, 720, 30, info.c300, Torus_Regular, anchor='mm')
            w_100 = datatext(1202, 720, 30, info.c100, Torus_Regular, anchor='mm')
            w_miss = datatext(1352, 720, 30, info.cmiss, Torus_Regular, anchor='mm')
        elif info.mode == 2:
            w_acc = datatext(1016, 625, 30, f'{info.acc * 100:.2f}%', Torus_Regular, anchor='mm')
            w_maxcb = datatext(1180, 625, 30, f'{info.maxcb:,}/{mapinfo.maxcb}', Torus_Regular, anchor='mm')
            w_pp = datatext(1344, 625, 30, pp, Torus_Regular, anchor='mm')
            w_300 = datatext(995, 720, 30, info.c300, Torus_Regular, anchor='mm')
            w_100 = datatext(1118, 720, 30, info.c100, Torus_Regular, anchor='mm')
            w_katu = datatext(1242, 720, 30, info.ckatu, Torus_Regular, anchor='mm')
            im = draw_text(im, w_katu)
            w_miss = datatext(1365, 720, 30, info.cmiss, Torus_Regular, anchor='mm')
        else:
            w_acc = datatext(935, 625, 30, f'{info.acc * 100:.2f}%', Torus_Regular, anchor='mm')
            w_maxcb = datatext(1130, 625, 30, f'{info.maxcb:,}', Torus_Regular, anchor='mm')
            w_pp = datatext(1328, 625, 30, f'{pp}/{ifpp}', Torus_Regular, anchor='mm')
            w_geki = datatext(886, 720, 30, info.cgeki, Torus_Regular, anchor='mm')
            im = draw_text(im, w_geki)
            w_300 = datatext(984, 720, 30, info.c300, Torus_Regular, anchor='mm')
            w_katu = datatext(1083, 720, 30, info.ckatu, Torus_Regular, anchor='mm')
            im = draw_text(im, w_katu)
            w_100 = datatext(1182, 720, 30, info.c100, Torus_Regular, anchor='mm')
            w_50 = datatext(1280, 720, 30, info.c50, Torus_Regular, anchor='mm')
            im = draw_text(im, w_50)
            w_miss = datatext(1378, 720, 30, info.cmiss, Torus_Regular, anchor='mm')
        im = draw_text(im, w_acc)
        im = draw_text(im, w_maxcb)
        im = draw_text(im, w_pp)
        im = draw_text(im, w_300)
        im = draw_text(im, w_100)
        im = draw_text(im, w_miss)

        score_outputimage = os.path.join(osufile, 'output', f'recent_{info.uid}.png')
        im.save(score_outputimage)
        msg = f'[CQ:image,file=file:///{score_outputimage}]'
    except Exception as e:
        log.error(f'制图错误：{e}')
        return f'Error: {type(e)}'
    return msg

async def best_pfm(id, mode: str, min: int, max: int, mods: list = []):  
    try:
        BPInfo = await OsuApi('bp', id, mode)
        if isinstance(BPInfo, str):
            return BPInfo
        info = ScoreInfo(BPInfo)
        info.BestBPScore(min, max, mods)
        if mods:
            if not info.modslist:
                return '没有在bp上查询到开启该mod的成绩'
            elif not info.modsbool:
                return f'在bp上查询到开启该mod成绩数量为{len(info.modslist)}个，少于{min}个'
        user = BPInfo[0]['user']['username']
        uid = BPInfo[0]['user_id']
        bplist_len = len(info.bpList)
        im = Image.new('RGBA', (1500, 180 + 82 * (bplist_len - 1)), (31, 41, 46, 255))
        bp_bg = os.path.join(osufile, 'Best Performance.png')
        BG_img = Image.open(bp_bg).convert('RGBA')
        im.alpha_composite(BG_img)
        f_div = Image.new('RGBA', (1500, 2), (255, 255, 255, 255)).convert('RGBA')
        im.alpha_composite(f_div, (0, 100))
        w_user = datatext(1450, 50, 25, f"{user}'s | {mode.capitalize()} | BP {min} - {max}", Torus_SemiBold, anchor='rm')
        im = draw_text(im, w_user)
        for num, bp in enumerate(info.bpList):
            h_num = 82 * num
            info.BestScore(bp)
            #mods
            if mods:
                for mods_num, s_mods in enumerate(mods):
                    mods_bg = os.path.join(osufile, 'mods', f'{s_mods}.png')
                    mods_img = Image.open(mods_bg).convert('RGBA')
                    im.alpha_composite(mods_img, (1000 + 50 * mods_num, 126 + h_num))
                if info.rank == 'X' or info.rank == 'S':
                    info.rank += 'H'
            #rank
            rank_img = os.path.join(osufile, 'ranking', f'ranking-{info.rank}.png')
            rank_bg = Image.open(rank_img).convert('RGBA').resize((64, 32))
            im.alpha_composite(rank_bg, (30, 128 + h_num))
            #曲名&作曲
            w_title_artist = datatext(100, 130 + h_num, 20, f'{info.title} | by {info.artist}', Meiryo_Regular, anchor='lm')
            im = draw_text(im, w_title_artist)
            #地图版本&时间
            old_time = datetime.strptime(info.date.replace('+00:00', ''), '%Y-%m-%dT%H:%M:%S')
            new_time = (old_time + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            w_version_time = datatext(100, 158 + h_num, 18, f'{info.version} | {new_time}', Torus_Regular, anchor='lm')
            im = draw_text(im, w_version_time, color=(238, 171, 0, 255))
            #acc
            w_acc = datatext(1250, 130 + h_num, 22, f'{info.acc * 100:.2f}%', Torus_SemiBold, anchor='lm')
            im = draw_text(im, w_acc, color=(238, 171, 0, 255))
            #mapid
            w_mapid = datatext(1250, 158 + h_num, 18, f'ID: {info.mapid}', Torus_Regular, anchor='lm')
            im = draw_text(im, w_mapid)
            #pp
            w_pp = datatext(1420, 140 + h_num, 25, int(info.pp), Torus_SemiBold, anchor='rm')
            im = draw_text(im, w_pp, (255, 102, 171, 255))
            w_n_pp = datatext(1450, 140 + h_num, 25, 'pp', Torus_SemiBold, anchor='rm')
            im = draw_text(im, w_n_pp, (209, 148, 176, 255))
            #分割线
            div = Image.new('RGBA', (1450, 2), (46, 53, 56, 255)).convert('RGBA')
            im.alpha_composite(div, (25, 180 + h_num))

        bp_outputimage = os.path.join(osufile, 'output', f'pfm_{uid}.png')
        im.save(bp_outputimage)
        msg = f'[CQ:image,file=file:///{bp_outputimage}]'
    except Exception as e:
        log.error(f'制图错误：{e}')
        return f'Error: {type(e)}'
    return msg

async def map_info(mapid, mods): 
    try:
        info = await OsuApi('map', mapid=mapid)
        if not info:
            return '未查询到该地图信息'
        if isinstance(info, str): 
            return info
        mapinfo = Beatmapset(info)
        diffinfo = calc_songlen(mapinfo.total_len), mapinfo.bpm, mapinfo.c_circles, mapinfo.c_sliders
        #获取地图
        dirpath = await MapDownload(mapinfo.setid)
        version_osu = get_osufile(dirpath, mapid, mapinfo.version)
        #获取音乐
        music = get_picmusic('music', version_osu)
        music_file = os.path.join(dirpath, music)
        if not os.path.isfile(music_file):
            shutil.rmtree(dirpath)
            await MapDownload(mapinfo.setid)
        music_url = f'{FILEHTTP}/{mapinfo.setid}/{music}'
        #pp
        if mapinfo.mode == 0:
            pp = calc_acc_pp(version_osu, mods)[5]
        elif mapinfo.mode == 3:
            pp = calc_mania_pp(version_osu, mods, 1000000)
        else:
            pp = 'Std & Mania Only'
        #计算时间
        if mapinfo.ranked_date:
            old_time = datetime.strptime(mapinfo.ranked_date.replace('+00:00', ''), '%Y-%m-%dT%H:%M:%S')
            new_time = (old_time + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
        else:
            new_time = 'No Ranked'
        #BG做地图
        im = Image.new('RGBA', (1200, 600))
        cover = get_picmusic('pic', version_osu)
        cover_url = f'{FILEHTTP}/{mapinfo.setid}/{cover}'
        cover_path = os.path.join(dirpath, cover)
        cover_crop = crop_bg('MB', cover_path)
        cover_img = ImageEnhance.Brightness(cover_crop).enhance(2 / 4.0)
        im.alpha_composite(cover_img)
        #获取地图info
        map_bg = os.path.join(osufile, 'beatmapinfo.png')
        mapbg = Image.open(map_bg).convert('RGBA')
        im.alpha_composite(mapbg)
        #模式
        diff_name = stars_diff(mapinfo.diff)
        mode_bg = get_modeimage(mapinfo.mode, diff_name)
        mode_img = Image.open(mode_bg).convert('RGBA').resize((50, 50))
        im.alpha_composite(mode_img, (50, 100))
        #cs - diff
        for num, i in enumerate(mapinfo.mapdiff):
            color = (255, 255, 255, 255)
            if num == 4:
                color = (255, 204, 34, 255)
            difflen = int(250 * i / 10) if i <= 10 else 250
            diff_len = Image.new('RGBA', (difflen, 8), color)
            im.alpha_composite(diff_len, (890, 426 + 35 * num))
            w_diff = datatext(1170, 426 + 35 * num, 20, i, Torus_SemiBold, anchor='mm')
            im = draw_text(im, w_diff)
        #mapper
        icon_url = f'https://a.ppy.sh/{mapinfo.uid}'
        user_icon = await get_projectimg(icon_url)
        icon = Image.open(user_icon).convert('RGBA').resize((100, 100))
        icon_img = draw_fillet(icon, 10)
        im.alpha_composite(icon_img, (50, 400))
        #mapid
        w_mapid = datatext(800, 40, 22, f'Setid: {mapinfo.setid}  |  Mapid: {mapid}', Torus_Regular, anchor='lm')
        im = draw_text(im, w_mapid)
        #版本
        w_version = datatext(120, 125, 25, mapinfo.version, Torus_SemiBold, anchor='lm')
        im = draw_text(im, w_version)
        #曲名
        w_title = datatext(50, 170, 30, mapinfo.title, Meiryo_SemiBold)
        im = draw_text(im, w_title)
        #曲师
        w_artist = datatext(50, 210, 25, f'by {mapinfo.artist}', Meiryo_SemiBold)
        im = draw_text(im, w_artist)
        #来源
        w_source = datatext(50, 260, 25, f'Source:{mapinfo.source}', Meiryo_SemiBold)
        im = draw_text(im, w_source)
        #mapper
        w_mapper_by = datatext(160, 400, 20, 'mapper by:', Torus_SemiBold)
        im = draw_text(im, w_mapper_by)
        w_mapper = datatext(160, 425, 20, mapinfo.mapper, Torus_SemiBold)
        im = draw_text(im, w_mapper)
        #ranked时间
        w_time_by = datatext(160, 460, 20, 'ranked by:', Torus_SemiBold)
        im = draw_text(im, w_time_by)
        w_time = datatext(160, 485, 20, new_time, Torus_SemiBold)
        im = draw_text(im, w_time)
        #状态
        w_status = datatext(1100, 304, 20, mapinfo.status.capitalize(), Torus_SemiBold, anchor='mm')
        im = draw_text(im, w_status)
        #时长 - 滑条
        for num, i in enumerate(diffinfo):
            w_info = datatext(770 + 120 * num, 365, 20, i, Torus_Regular, anchor='lm')
            im = draw_text(im, w_info, (255, 204, 34, 255))
        #maxcb
        w_mapcb = datatext(50, 570, 20, f'Max Combo: {mapinfo.maxcb}', Torus_SemiBold, anchor='lm')
        im = draw_text(im, w_mapcb)
        #pp
        w_pp = datatext(320, 570, 20, f'SS PP: {pp}', Torus_SemiBold, anchor='lm')
        im = draw_text(im, w_pp)
        #音乐
        musicinfo = f'[CQ:music,type=custom,url=https://osu.ppy.sh/b/{mapid},audio={music_url},title={mapinfo.artist} - {mapinfo.title},content=点击可跳转该地图链接查看详情,image={cover_url}]'
        #输出
        map_osuputimage = os.path.join(osufile, 'output', 'info_map.png')
        im.save(map_osuputimage)
        msg = f'[CQ:image,file=file:///{map_osuputimage}]'
        return musicinfo, msg
    except Exception as e:
        log.error(f'制图错误：{e}')
        return f'Error:{type(e)}'

async def search_map(project, mode, status, keyword, op=False):
    try:
        if not op:
            mode, status = sayo[mode], sayo[status]
            sayoinfo = await SayoApi(project, mode, status, keyword)
            if sayoinfo['status'] == -1:
                return '未查询到地图'
            elif isinstance(sayoinfo, str):
                return sayoinfo          
            data = sayoinfo['data']
        else:
            chumiinfo = await ChimuApi(mode, chimu[status], keyword)
            if not chumiinfo:
                return '未查询到地图'
            elif isinstance(chumiinfo, str):
                return chumiinfo
            data = chumiinfo
        # 并发
        info = []
        tasks = []
        async def sayo_mapinfo(setid):
            try:
                sayoinfo = await SayoApi('mapinfo', setid=setid)
                info.append(sayoinfo)
            except Exception as e:
                log.error(e)
                raise '请求过程中出错'
        # loop
        loop = asyncio.get_event_loop()
        for temp_sid in data:
            if not op:
                task = loop.create_task(sayo_mapinfo(temp_sid['sid']))
            else:
                task = loop.create_task(sayo_mapinfo(temp_sid['SetID']))
            tasks.append(task)
            await asyncio.sleep(0.1)
        
        await asyncio.sleep(1)
        for _ in tasks:
            _.cancel()
        # end
        #根据结果定高度
        num = len(data)
        im_h = num * 303 - 3 if num != 1 else num * 300
        im = Image.new('RGBA', (1200, im_h))
        for infonum, map in enumerate(data):
            #每个结果增加高度
            pnum = 303 * infonum
            if not op:
                songinfo = SayoInfo(map)
            else:
                songinfo = ChumiInfo(map)
            #查图
            songinfo.map(info[infonum]['data'])
            #获取背景
            coverurl = f'https://assets.ppy.sh/beatmaps/{songinfo.setid}/covers/cover@2x.jpg'
            cover = await get_projectimg(coverurl)
            #裁切
            cover_crop = crop_bg('MP', cover)
            cover_gb = cover_crop.filter(ImageFilter.GaussianBlur(1))
            cover_img = ImageEnhance.Brightness(cover_gb).enhance(2 / 4.0)
            im.alpha_composite(cover_img, (0, pnum))
            #mode图片
            gmap = sorted(songinfo.gmap, key=lambda k: k['star'], reverse=False)
            for num, cmap in enumerate(gmap):
                if num < 10:
                    songinfo.mapinfo(cmap)
                    diffname = stars_diff(songinfo.star)
                    mode_bg = get_modeimage(songinfo.mode, diffname)
                    mode_img = Image.open(mode_bg).convert('RGBA').resize((50, 50))
                    im.alpha_composite(mode_img, (25 + 60 * num, 215  + pnum))
                    w_diff = datatext(50 + 60 * num, 280 + pnum, 20, songinfo.star, Torus_SemiBold, anchor='mm')
                    im = draw_text(im, w_diff)
                else:
                    plusnum = f'+{num-9}'
            if num >= 10:
                w_mode_num = datatext(650, 250 + pnum, 25, plusnum, Torus_SemiBold)
                im = draw_text(im, w_mode_num)
            #曲名
            w_title = datatext(25, 40 + pnum, 40, songinfo.title, Meiryo_SemiBold)
            im = draw_text(im, w_title)
            #曲师
            w_artist = datatext(25, 75 + pnum, 20, songinfo.artist, Meiryo_SemiBold)
            im = draw_text(im, w_artist)
            #mapper
            w_mapper = datatext(25, 110 + pnum, 20, f'mapper by {songinfo.mapper}', Torus_SemiBold)
            im = draw_text(im, w_mapper)
            #rank时间
            if songinfo.apptime == -1:
                songinfo.apptime = 'No Ranked'
            else:
                datearray = datetime.utcfromtimestamp(songinfo.apptime)
                songinfo.apptime = (datearray + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
            w_apptime = datatext(25, 145 + pnum, 20, f'Approved Time: {songinfo.apptime}', Torus_SemiBold)
            im = draw_text(im, w_apptime)
            #来源
            w_source = datatext(25, 180 + pnum, 20, f'Source: {songinfo.source}', Meiryo_SemiBold)
            im = draw_text(im, w_source)
            #bpm
            w_bpm = datatext(1150, 110 + pnum, 20, f'BPM: {songinfo.bpm}', Torus_SemiBold, anchor='rt')
            im = draw_text(im, w_bpm)
            #曲长
            music_len = calc_songlen(songinfo.songlen)
            w_music_len = datatext(1150, 145 + pnum, 20, f'lenght: {music_len}', Torus_SemiBold, anchor='rt')
            im = draw_text(im, w_music_len)
            #setid
            w_setid = datatext(1150, 20 + pnum, 20, f'Setid: {songinfo.setid}', Torus_SemiBold, anchor='rt')
            im = draw_text(im, w_setid)
            ims = Image.new('RGBA', (1200, 3), (255, 255, 255, 255))
            im.alpha_composite(ims, (0, 303 * (infonum + 1) - 3))

        outputimage_path = os.path.join(osufile, 'output', 'search.png')
        im.save(outputimage_path)
        msg = f'[CQ:image,file=file:///{outputimage_path}]' 
    except Exception as e:
        log.error(f'制图错误：{e}')
        return f'Error: {type(e)}'
    return msg

async def bmap_info(mapid, op=False):
    if op:
        info = await OsuApi('map', mapid=mapid)
        if not info:
            return '未查询到地图'
        elif isinstance(info, str):
            return info
        mapid = info['beatmapset_id']
    info = await SayoApi('mapinfo', setid=mapid)
    if info['status'] == -1:
        return '未查询到地图'
    elif isinstance(info, str):
        return info
    try:
        songinfo = SayoInfo(info['data'])
        songinfo.map(info['data'])
        coverurl = f'https://assets.ppy.sh/beatmaps/{mapid}/covers/cover@2x.jpg'
        cover = await get_projectimg(coverurl)
        #新建
        if len(songinfo.gmap) > 20:
            im_h = 400 + 102 * 20
        else:
            im_h = 400 + 102 * (len(songinfo.gmap) - 1)
        im = Image.new('RGBA', (1200, im_h), (31, 41, 46, 255))
        #背景
        cover_crop = crop_bg('MP', cover)
        cover_gb = cover_crop.filter(ImageFilter.GaussianBlur(1))
        cover_img = ImageEnhance.Brightness(cover_gb).enhance(2 / 4.0)
        im.alpha_composite(cover_img, (0, 0))
        #曲名
        w_title = datatext(25, 40, 40, songinfo.title, Meiryo_SemiBold)
        im = draw_text(im, w_title)
        #曲师
        w_artist = datatext(25, 75, 20, songinfo.artist, Meiryo_SemiBold)
        im = draw_text(im, w_artist)
        #mapper
        w_mapper = datatext(25, 110, 20, f'mapper by {songinfo.mapper}', Torus_SemiBold)
        im = draw_text(im, w_mapper)
        #rank时间
        if songinfo.apptime == -1:
            songinfo.apptime = 'No Ranked'
        else:
            datearray = datetime.utcfromtimestamp(songinfo.apptime)
            songinfo.apptime = (datearray + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
        w_apptime = datatext(25, 145, 20, f'Approved Time: {songinfo.apptime}', Torus_SemiBold)
        im = draw_text(im, w_apptime)
        #来源
        w_source = datatext(25, 180, 20, f'Source: {songinfo.source}', Meiryo_SemiBold)
        im = draw_text(im, w_source)
        #bpm
        w_bpm = datatext(1150, 110, 20, f'BPM: {songinfo.bpm}', Torus_SemiBold, anchor='rt')
        im = draw_text(im, w_bpm)
        #曲长
        music_len = calc_songlen(songinfo.songlen)
        w_music_len = datatext(1150, 145, 20, f'lenght: {music_len}', Torus_SemiBold, anchor='rt')
        im = draw_text(im, w_music_len)
        #Setid
        w_setid = datatext(1150, 20, 20, f'Setid: {mapid}', Torus_SemiBold, anchor='rt')
        im = draw_text(im, w_setid)
        gmap = sorted(songinfo.gmap, key=lambda k: k['star'], reverse=False)
        for num, cmap in enumerate(gmap):
            if num < 20:
                h_num = 102 * num
                songinfo.mapinfo(cmap)
                #难度
                diff_name = stars_diff(songinfo.star)
                mode_bg = get_modeimage(songinfo.mode, diff_name)
                mode_img = Image.open(mode_bg).convert('RGBA').resize((20, 20))
                im.alpha_composite(mode_img, (20, 320 + h_num))
                #星星
                stars_bg = os.path.join(osufile, 'work', f'stars_{diff_name}.png')
                stars_img = Image.open(stars_bg).convert('RGBA').resize((20, 20))
                im.alpha_composite(stars_img, (50, 320 + h_num))
                #diff
                bar_bg = os.path.join(osufile, 'work', 'bmap.png')
                bar_img = Image.open(bar_bg).convert('RGBA')
                im.alpha_composite(bar_img, (10, 365 + h_num))
                gc = ['CS', 'HP', 'OD', 'AR']
                for num, i in enumerate(songinfo.diff):
                    diff_len = int(200 * i / 10) if i <= 10 else 200
                    diff_bg = Image.new('RGBA', (diff_len, 12), (255, 255, 255, 255))
                    im.alpha_composite(diff_bg, (50 + 300 * num, 365 + h_num))
                    w_d_name = datatext(20 + 300 * num, 369 + h_num, 20, gc[num], Torus_SemiBold, anchor='lm')
                    im = draw_text(im, w_d_name)
                    w_diff = datatext(265 + 300 * num, 369 + h_num, 20, i, Torus_SemiBold, anchor='lm')
                    im = draw_text(im, w_diff, (255, 204, 34, 255))
                    if num != 3:
                        w_d = datatext(300 + 300 * num, 369 + h_num, 20, '|', Torus_SemiBold, anchor='lm')
                        im = draw_text(im, w_d)
                #难度
                w_star = datatext(80, 328 + h_num, 20, songinfo.star, Torus_SemiBold, anchor='lm')
                im = draw_text(im, w_star)
                #version
                w_version = datatext(125, 328 + h_num, 20, f' |  {songinfo.version}', Torus_SemiBold, anchor='lm')
                im = draw_text(im, w_version)
                #mapid
                w_mapid = datatext(1150, 328 + h_num, 20, f'Mapid: {songinfo.bid}', Torus_SemiBold, anchor='rm')
                im = draw_text(im, w_mapid)
                #maxcb
                w_maxcb = datatext(700, 328 + h_num, 20, f'Max Combo: {songinfo.maxcb}', Torus_SemiBold, anchor='lm')
                im = draw_text(im, w_maxcb)
                #分割线
                div = Image.new('RGBA', (1150, 2), (46, 53, 56, 255)).convert('RGBA')
                im.alpha_composite(div, (25, 400 + h_num))
            else:
                plusnum = f'+ {num-19}'
        if num >= 20:
            w_plusnum = datatext(600, 350 + 102 * 20, 50, plusnum, Torus_SemiBold, anchor='mm')
            im = draw_text(im, w_plusnum)
        outputimage_path = os.path.join(osufile, 'output', 'bmapinfo.png')
        im.save(outputimage_path)
        msg = f'[CQ:image,file=file:///{outputimage_path}]'
    except Exception as e:
        log.error(f'制图错误：{e}')
        return f'Error: {type(e)}'
    return msg

async def bindinfo(project, id, qid):
    info = await OsuApi(project, id, GM[0])
    if not info:
        return '未查询到该玩家'
    elif isinstance(info, str):
        return info
    uid = info['id']
    name = info['username']
    esql.insert_user(qid, uid, name)
    await user(uid)
    msg = f'用户 {name} 已成功绑定QQ {qid}'
    return msg

async def update_icon(project, id, mode):
    info = await OsuApi(project, id, mode)
    if not info:
        return '未查询到该玩家'
    elif isinstance(info, str):
        return info
    icon = info['avatar_url']
    header = info['cover_url']
    icon_t = await get_projectimg(icon, 'icon', id, True)
    header_t = await get_projectimg(header, 'header', id, True)
    if icon_t and header_t:
        return '头像和头图更新完毕'
    else:
        return '头像和头图更新失败'

async def get_map_bg(mapid):
    info = await OsuApi('map', mapid=mapid)
    if not info:
        return '未查询到该地图'
    elif isinstance(info, str):
        return info
    version = info['version']
    setid = info['beatmapset_id']
    dirpath = await MapDownload(setid)
    version_osu = get_osufile(dirpath, mapid, version)
    path = get_picmusic('pic', version_osu)
    msg = f'[CQ:image,file=file:///{os.path.join(dirpath, path)}]'
    return msg

async def user(id, update=False):
    for mode in range(0, 4):
        if not update:
            new = esql.get_all_newinfo(id, mode)
            if new:
                continue
        userinfo = await OsuApi('update', id, GM[mode])
        info = UserInfo(userinfo)
        if info.play_count != 0:
            if update:
                esql.update_all_info(id, info.crank, info.grank, info.pp, info.acc, info.play_count, info.play_hits, mode)
            else:
                esql.insert_all_info(id, info.crank, info.grank, info.pp, info.acc, info.play_count, info.play_hits, mode)
        else:
            if update:
                esql.update_all_info(id, 0, 0, 0, 0, 0, 0, mode)
            else:
                esql.insert_all_info(id, 0, 0, 0, 0, 0, 0, mode)
        log.info(f'玩家:[{info.username}] {GM[mode]}模式 个人信息更新完毕')
