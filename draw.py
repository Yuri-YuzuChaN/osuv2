from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import os, time

from .api import get_api_info
from .file import *
from .pp import *
from .mods import *
from .sql import osusql

osupath = os.path.dirname(__file__)
osufile = f'{osupath}/osufile/'
mapfile = f'{osufile}map/'
icon = f'{osufile}icon/'

Torus_Regular = os.path.join(osufile, 'fonts', 'Torus Regular.otf')
Torus_SemiBold = os.path.join(osufile, 'fonts', 'Torus SemiBold.otf')
Venera = os.path.join(osufile, 'fonts', 'Venera.otf')
Weiruan = os.path.join(osufile, 'fonts', 'msyh.ttc')

GM = {0 : 'osu', 1 : 'taiko', 2 : 'fruits', 3 : 'mania'}
GMN = {'osu' : 'Std', 'taiko' : 'Taiko', 'fruits' : 'Ctb', 'mania' : 'Mania'}
FGM = {'osu' : 0 , 'taiko' : 1 , 'fruits' : 2 , 'mania' : 3}

class picture:
    def __init__(self, L, T, Path):
        self.L = L
        self.T = T
        self.path = Path
        
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
            return '↑', num * -1
        else:
            return '↓', num * -1
    elif num > 0:
        if rank:
            return '↓', num
        elif pp:
            return '↑', num
        else:
            return '+', num
    else:
        return '', 0

def wedge_acc(acc, id):
    size = [acc, 100-acc]
    insize = [60, 20, 7, 7, 5, 1]
    insizecolor = ['#ff5858', '#ea7948', '#d99d03', '#72c904', '#0096a2', '#be0089']
    fig, ax = plt.subplots()
    patches, texts = ax.pie(size, radius=1.1, startangle=90, counterclock=False, pctdistance=0.9, wedgeprops=dict(width=0.27))
    ax.pie(insize, radius=0.8, colors=insizecolor, startangle=90, counterclock=False, pctdistance=0.9, wedgeprops=dict(width=0.05))
    patches[1].set_alpha(0)
    path = f'{osufile}/output/{id}_acc.png'
    plt.savefig(path, transparent=True)
    return path

def crop_bg(path, size):
    bg = Image.open(path).convert('RGBA')
    bg_w = bg.size[0]
    bg_h = bg.size[1]
    if size == 'BG':
        fix_w = 1000
        fix_h = 240
    elif size == 'H':
        fix_w = 360
        fix_h = 120
    elif size == 'HI':
        fix_w = 1000
        fix_h = 400
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
        return path

def stars_diff(stars):
    diff = ''
    if 0 < stars < 2.0:
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

def set_mod_list(json, mods):
    vnum =[]
    for index, v in enumerate(json):
        if v['mods']:
            num = get_mods_num(v['mods'])
            if num == mods:
                vnum.append(index)
    return vnum

async def draw_info(id, mode):
    try:
        info = await get_api_info('info', id, mode)
        if not info:
            return '未查询到该玩家'
        pc = info['statistics']['play_count']
        if pc == 0:
            return f'此玩家尚未游玩过{GMN[mode]}模式'
        esql = osusql()
        icon = info['avatar_url']
        country_code = info['country_code']
        uid = info['id']
        userstatus = info['is_online']
        supporter = info['is_supporter']
        name = info['username']
        coverurl = info['cover_url']
        badges = info['badges']
        play = info['statistics']
        level = play['level']
        current = level['current']
        progress = level['progress']
        grank = play['global_rank']
        pp = play['pp']
        r_score = play['ranked_score']
        acc = round(play['hit_accuracy'], 2)
        pc = play['play_count']
        play_time = play['play_time']
        t_score = play['total_score']
        count = play['total_hits']
        g_counts = play['grade_counts']
        gc = g_counts['ssh'], g_counts['ss'], g_counts['sh'], g_counts['s'], g_counts['a']
        crank = play['country_rank']
        #对比
        result = esql.get_all_newinfo(uid, FGM[mode])
        if result:
            for i in result:
                n_crank = i[2]
                n_grank = i[3]
                n_pp = i[4]
                n_acc = i[5]
                n_pc = i[6]
                n_count = i[7]
        else:
            n_crank, n_grank, n_pp, n_acc, n_pc, n_count = 0, 0, 0, 0, 0, 0
        #新建
        info_bg = os.path.join(osufile, 'info.png')
        im = Image.new('RGBA', (1000, 1222))
        #获取头图，头像，地区，状态，supporter
        user_header = await get_project_img('header', coverurl, uid)
        user_icon = await get_project_img('icon', icon, uid)
        country = os.path.join(osufile, 'flags', f'{country_code}.png')
        status = os.path.join(osufile, 'work', 'on-line.png' if userstatus else 'off-line.png')
        user_supporter = os.path.join(osufile, 'work', 'suppoter.png')
        exp_l = os.path.join(osufile, 'work', 'left.png')
        exp_c = os.path.join(osufile, 'work', 'center.png')
        exp_r = os.path.join(osufile, 'work', 'right.png')
        #头图
        header_img = crop_bg(user_header, 'HI')
        im.alpha_composite(header_img, (0, 100))
        #底图
        info_img = Image.open(info_bg).convert('RGBA')
        im.alpha_composite(info_img)
        #头像
        icon_bg = Image.open(user_icon).convert('RGBA').resize((300, 300))
        icon_img = draw_fillet(icon_bg, 25)
        im.alpha_composite(icon_img, (50, 148))
        # #模式
        
        #地区
        country_bg = Image.open(country).convert('RGBA').resize((80, 54))
        im.alpha_composite(country_bg, (400, 394))
        #supporter
        if supporter:
            supporter_bg = Image.open(user_supporter).convert('RGBA').resize((80, 80))
            im.alpha_composite(supporter_bg, (400, 300))
        #经验
        if progress != 0:  
            exp_left_bg = Image.open(exp_l).convert('RGBA')
            im.alpha_composite(exp_left_bg, (50, 544))
            exp_width = progress * 7 - 3
            exp_center_bg = Image.open(exp_c).convert('RGBA').resize((exp_width ,10))
            im.alpha_composite(exp_center_bg, (54, 544))
            exp_right_bg = Image.open(exp_r).convert('RGBA')
            im.alpha_composite(exp_right_bg, (int(54 + exp_width), 544))
        #模式
        w_mode = datatext(935, 50, 45, GMN[mode], Torus_Regular, anchor='rm')
        im = draw_text(im, w_mode)
        #玩家名
        w_name = datatext(400, 205, 50, name, Torus_Regular, anchor='lm')
        im = draw_text(im, w_name)
        #地区排名
        w_crank = datatext(495, 448, 30, '#{:,}'.format(crank), Torus_Regular, anchor='lb')
        im = draw_text(im, w_crank)
        op, value = info_calc(crank, n_crank, rank=True)
        if value != 0:
            w_n_crank = datatext(610, 448, 25, f'({op}{value})', Weiruan, anchor='lb')
            im = draw_text(im, w_n_crank)
        #等级
        w_current = datatext(900, 548, 25, current, Torus_Regular, anchor='mm')
        im = draw_text(im, w_current)
        #经验百分比
        w_progress = datatext(750, 560, 20, f'{progress}%', Torus_Regular, anchor='rt')
        im = draw_text(im, w_progress)
        #全球排名
        w_grank = datatext(55, 685, 35, f'#{format(grank, ",")}', Torus_Regular)
        im = draw_text(im, w_grank)
        op, value = info_calc(grank, n_grank, rank=True)
        if value != 0:
            w_n_grank = datatext(65, 720, 20, f'{op}{value}', Weiruan)
            im = draw_text(im, w_n_grank)
        #pp
        w_pp = datatext(295, 685, 35, format(pp, ","), Torus_Regular)
        im = draw_text(im, w_pp)
        op, value = info_calc(pp, n_pp, pp=True)
        if value != 0:
            w_n_pc = datatext(305, 720, 20, '{op}{:.2f}'.format(op, value), Weiruan)
            im = draw_text(im, w_n_pc)
        #SS - A
        gc_x = 493
        for i in gc:
            w_ss_a = datatext(gc_x, 675, 30, format(i, ","), Torus_Regular, anchor='mt')
            im = draw_text(im, w_ss_a)
            gc_x+=100
        #rank分
        w_r_score = datatext(935, 795, 40, format(r_score, ","), Torus_Regular, anchor='rt')
        im = draw_text(im, w_r_score)
        #acc
        op, value = info_calc(acc, n_acc)
        t_acc = '{:.2f}%({}{:.2f}%)'.format(acc, op, value) if value != 0 else '{:.2f}%'.format(acc)
        w_acc = datatext(935, 865, 40, t_acc, Torus_Regular, anchor='rt')
        im = draw_text(im, w_acc)
        #游玩次数
        op, value = info_calc(pc, n_pc)
        t_pc = '{:,}({}{:,})'.format(pc, op, value) if value != 0 else format(pc, ",")
        w_pc = datatext(935, 935, 40, t_pc, Torus_Regular, anchor='rt')
        im = draw_text(im, w_pc)
        #总分
        w_t_score = datatext(935, 1005, 40, format(t_score, ","), Torus_Regular, anchor='rt')
        im = draw_text(im, w_t_score)
        #总命中
        op, value = info_calc(count, n_count)
        t_count = '{:,}({}{:,})'.format(count, op, value) if value != 0 else format(count, ",")
        w_conut = datatext(935, 1075, 40, t_count, Torus_Regular, anchor='rt')
        im = draw_text(im, w_conut) 
        #游玩时间
        sec = timedelta(seconds = play_time)
        d_time = datetime(1, 1, 1, 1) + sec
        t_time = "%dd %dh %dm %ds" % (d_time.day-1, d_time.hour, d_time.minute, d_time.second)
        w_name = datatext(935, 1145, 40, t_time, Torus_Regular, anchor='rt')
        im = draw_text(im, w_name)
        #输出
        outputimage_path = os.path.join(osufile, 'output', f'info_{uid}.png')
        im.save(outputimage_path)
        msg = f'[CQ:image,file=file:///{outputimage_path}]'
    except Exception as e:
        return f'Error: {e}'
    return msg

async def draw_score(project, id, mode, **vkargs):
    try:
        if project == 'recent':
            info = await get_api_info(project, id, mode)
            if not info:
                return '未查询到最近游玩的记录'
            elif isinstance(info, str):
                return info
            userscore = info[0]
        elif project == 'bp':
            info = await get_api_info(project, id, mode)
            if not info:
                return '未查询到bp成绩'
            elif isinstance(info, str):
                return info
            bp = vkargs['bp']
            try:
                setmods = get_mods_num(vkargs['mods'])
                modslist = set_mod_list(info, setmods)
                if not modslist:
                    return '没有在bp上查询到开启该mod的成绩'
                userscore = info[modslist[bp-1]]
            except KeyError:
                userscore = info[bp-1]
        elif project == 'score':
            info = await get_api_info(project, id, mode, mapid=vkargs['mapid'])
            if not info:
                return '未查询到该地图的成绩'
            elif isinstance(info, str):
                return info
            grank = f'#{format(info["position"], ",")}'
            userscore = info['score']
            mapid = userscore['beatmap']['id']
            headericon = userscore['user']['cover']['url']
        else:
            return False
    except Exception as e:
        return f'Error: {e}'
    try:
        #score
        uid = userscore['user_id']
        acc = userscore['accuracy']
        mods = userscore['mods']
        score = userscore['score']
        maxcb = userscore['max_combo']
        count = userscore['statistics']    ####
        mode = userscore['mode_int']
        #cb
        c50 = count['count_50']
        c100 = count['count_100']
        c300 = count['count_300']
        cgeki = count['count_geki']
        ckatu = count['count_katu']
        cmiss = count['count_miss']
        rank = userscore['rank']
        date = userscore['created_at']
        pp = userscore['pp']
        #map
        mapsetid = userscore['beatmap']['beatmapset_id']
        mapid = userscore['beatmap']['id']
        #beatmapset
        mapinfo = await get_api_info('map', mapid=mapid)
        total_len = mapinfo['total_length']
        version = mapinfo['version']
        diff = mapinfo['difficulty_rating']
        od = mapinfo['accuracy']
        ar = mapinfo['ar']
        cs = mapinfo['cs']
        hp = mapinfo['drain']
        bpm = mapinfo['bpm']
        map = mapinfo['beatmapset']
        artist = map['artist']
        if artist == None:
            artist = ['artist']
        title = map['title']
        if title == None:
            title = ['title']
        mapper = map['creator']
        coverurl = map['covers']['cover']
        #user
        user = userscore['user']        ####
        icon = user['avatar_url']
        country_code = user['country_code']
        userstatus = user['is_online']
        supporter = user['is_supporter']
        name = user['username']
        if project == 'bp' or project == 'recent':
            header = await get_api_info('info', id=uid, mode='osu')
            headericon = header['cover_url']
            grank = '--'
        #下载地图
        dirpath = await MapDownload(mapsetid)
        #获取文件
        version_osu = get_file(dirpath, mapid, version)
        #pp
        if project == 'recent' and mode == 0:
            setmods = 0
            if mods:
                setmods = get_mods_num(mods)
            pp, aim_pp, speed_pp, acc_pp = calc_pp(version_osu, setmods, maxcb, c50, c100, c300, cmiss)
        elif project == 'recent' and mode != 0:
            pp, aim_pp, speed_pp, acc_pp = '--', '--', '--', '--'
        else:
            pp, aim_pp, speed_pp, acc_pp = int(pp), '--', '--', '--'
        #新建图片
        im = Image.new('RGBA', (1000, 532))
        #获取cover并裁剪，高斯，降低亮度
        cover = await get_project_img('cover', coverurl, mapid)
        cover_crop = crop_bg(cover, 'BG')
        cover_gb = cover_crop.filter(ImageFilter.GaussianBlur(1))
        cover_img = ImageEnhance.Brightness(cover_gb).enhance(2 / 4.0)
        im.alpha_composite(cover_img, (0, 133))
        #获取成绩背景做底图
        BG = get_mode_img(mode)
        recent_bg = Image.open(BG).convert('RGBA')
        im.alpha_composite(recent_bg)
        #模式
        diff_name = stars_diff(diff)
        mode_bg = get_mode_img(mode, diff_name)
        mode_img = Image.open(mode_bg).convert('RGBA').resize((20, 20))
        im.alpha_composite(mode_img, (50, 101))
        #难度星星
        stars_bg = os.path.join(osufile, 'work', f'stars_{diff_name}.png')
        stars_img = Image.open(stars_bg).convert('RGBA').resize((15, 15))
        im.alpha_composite(stars_img, (89, 105))
        #mods
        if mods:
            mods_num = 332
            for s_mods in mods:
                mods_bg = os.path.join(osufile, 'mods', f'{s_mods}.png')
                mods_img = Image.open(mods_bg).convert('RGBA').resize((30, 20))
                im.alpha_composite(mods_img, (mods_num, 160))
                mods_num += 6
            ranking = ['XH', 'SH', 'A', 'B', 'C', 'D', 'F']
            if rank == 'X' or rank == 'S':
                rank = rank + 'H'
        else:
            ranking = ['X', 'S', 'A', 'B', 'C', 'D', 'F']
        #成绩S-F
        rank_num = 162
        rank_ok = False
        for i in ranking:
            rank_img = os.path.join(osufile, 'ranking', f'ranking-{i}.png')
            if rank_ok:
                rank_b = Image.open(rank_img).convert('RGBA').resize((32, 16))
                rank_new = Image.new('RGBA', rank_b.size, (0,0,0,0))
                rank_bg = Image.blend(rank_new, rank_b, 0.5)
            elif i != rank:
                rank_b = Image.open(rank_img).convert('RGBA').resize((32, 16))
                rank_new = Image.new('RGBA', rank_b.size, (0,0,0,0))
                rank_bg = Image.blend(rank_new, rank_b, 0.2)
            else:
                rank_bg = Image.open(rank_img).convert('RGBA').resize((32, 16))
                rank_ok = True
                if mods:
                    if rank == 'XH' or rank == 'SH':
                        rank = rank[:-1]
            im.alpha_composite(rank_bg, (50, rank_num))
            rank_num += 26
        #成绩+acc
        score_acc = wedge_acc(acc * 100, uid)
        score_acc_bg = Image.open(score_acc).convert('RGBA').resize((384, 288))
        im.alpha_composite(score_acc_bg, (10, 102))
        #获取头图，头像，地区，状态，support
        user_headericon = await get_project_img('header', headericon, uid)
        user_icon = await get_project_img('icon', icon, uid)
        country = os.path.join(osufile, 'flags', f'{country_code}.png')
        status = os.path.join(osufile, 'work', 'on-line.png' if userstatus else 'off-line.png')
        user_supporter = os.path.join(osufile, 'work', 'suppoter.png')
        #头图
        headericon_crop = crop_bg(user_headericon, 'H')
        headericon_d = draw_fillet(headericon_crop, 10)
        headericon_gb = headericon_d.filter(ImageFilter.GaussianBlur(1))
        headericon_img = ImageEnhance.Brightness(headericon_gb).enhance(2 / 4.0)
        im.alpha_composite(headericon_img, (50, 394))
        #头像
        icon_bg = Image.open(user_icon).convert('RGBA').resize((60, 60))
        icon_img = draw_fillet(icon_bg, 10)
        im.alpha_composite(icon_img, (60, 404))
        #地区
        country_bg = Image.open(country).convert('RGBA').resize((39, 26))
        im.alpha_composite(country_bg, (130, 404))
        #在线状态
        status_bg = Image.open(status).convert('RGBA').resize((30, 30))
        im.alpha_composite(status_bg, (76, 475))
        #supporter
        if supporter:
            supporter_bg = Image.open(user_supporter).convert('RGBA').resize((26, 26))
            im.alpha_composite(supporter_bg, (178, 404))
        #mapid
        w_mapid = datatext(950, 31, 18, f'Mapid: {mapid}', Torus_Regular, anchor='rm')
        im = draw_text(im, w_mapid)
        #曲名
        w_title = datatext(50, 79, 20, f'{title} | by {artist}', Torus_SemiBold, anchor='lm')
        im = draw_text(im, w_title)
        #星级
        w_diff = datatext(107, 112, 12, diff, Torus_SemiBold, anchor='lm')
        im = draw_text(im, w_diff)
        #谱面版本，mapper
        w_version = datatext(150, 112, 15, f'{version} | mapper by {mapper}', Torus_SemiBold, anchor='lm')
        im = draw_text(im, w_version)
        #评价
        w_rank = datatext(206, 251, 50, rank, Venera, anchor='mm')
        im = draw_text(im, w_rank)
        #cs, ar, od, hp, bpm, mapcb
        if mode != 3:
            map_maxcb = format(mapinfo['max_combo'], ',')
        else:
            map_maxcb = '--'
        map_diff = f'CS: {cs}  AR: {ar}  OD: {od}  HP: {hp} BPM: {bpm}  COMBO: {map_maxcb}'
        w_map_diff = datatext(950, 112, 15, map_diff, Torus_Regular, anchor='rm')
        im = draw_text(im, w_map_diff)
        #分数
        w_score = datatext(332, 211, 50, format(score, ','), Torus_Regular, anchor='lm')
        im = draw_text(im, w_score)
        #玩家
        w_played = datatext(332, 264, 12, 'Played by:', Torus_SemiBold, anchor='lm')
        im = draw_text(im, w_played)
        w_username = datatext(420, 264, 12, name, Torus_SemiBold, anchor='lm')
        im = draw_text(im, w_username)
        #时间
        w_date = datatext(332, 281, 12, 'Submitted on:', Torus_SemiBold, anchor='lm')
        im = draw_text(im, w_date)
        old_time = datetime.strptime(date.replace('+00:00', ''), '%Y-%m-%dT%H:%M:%S')
        new_time = (old_time + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
        w_time = datatext(420, 281, 12, new_time, Torus_SemiBold, anchor='lm')
        im = draw_text(im, w_time)
        #全球排名
        w_grank = datatext(342, 331, 16, grank, Torus_SemiBold, anchor='lm')
        im = draw_text(im, w_grank)
        #左下玩家名
        w_l_username = datatext(130, 447, 16, name, Torus_SemiBold, anchor='lm')
        im = draw_text(im, w_l_username)
        #在线，离线
        w_line = datatext(130, 488, 20, 'online' if userstatus else 'offline', Torus_SemiBold, anchor='lm')
        im = draw_text(im, w_line)
        #acc,cb,pp,300,100,50,miss
        if mode == 0:
            # pfm_x = [699, 799, 900, 686, 761, 836, 911]
            w_acc = datatext(700, 420, 20, '{:.2f}%'.format(acc * 100), Torus_Regular, anchor='mm')
            w_maxcb = datatext(799, 420, 20, f'{format(maxcb, ",")}x', Torus_Regular, anchor='mm')
            w_pp = datatext(901, 420, 20, pp, Torus_Regular, anchor='mm')
            w_300 = datatext(687, 480, 20, c300, Torus_Regular, anchor='mm')
            w_100 = datatext(763, 480, 20, c100, Torus_Regular, anchor='mm')
            w_50 = datatext(838, 480, 20, c50, Torus_Regular, anchor='mm')
            im = draw_text(im, w_50)
            w_miss = datatext(912, 480, 20, cmiss, Torus_Regular, anchor='mm')
        elif mode == 1:
            # pfm_x = [699, 799, 900, 699, 799, 900]
            w_acc = datatext(699, 420, 20, '{:.2f}%'.format(acc * 100), Torus_Regular, anchor='mm')
            w_maxcb = datatext(799, 420, 20, f'{format(maxcb, ",")}x', Torus_Regular, anchor='mm')
            w_pp = datatext(900, 420, 20, pp, Torus_Regular, anchor='mm')
            w_300 = datatext(699, 480, 20, c300, Torus_Regular, anchor='mm')
            w_100 = datatext(799, 480, 20, c100, Torus_Regular, anchor='mm')
            w_miss = datatext(900, 480, 20, cmiss, Torus_Regular, anchor='mm')
        elif mode == 2:
            # pfm_x = [676, 785, 894, 663, 745, 827, 909]
            w_acc = datatext(677, 420, 20, '{:.2f}%'.format(acc * 100), Torus_Regular, anchor='mm')
            w_maxcb = datatext(786, 420, 20, f'{format(maxcb, ",")}x', Torus_Regular, anchor='mm')
            w_pp = datatext(896, 420, 20, pp, Torus_Regular, anchor='mm')
            w_300 = datatext(663, 480, 20, c300, Torus_Regular, anchor='mm')
            w_100 = datatext(746, 480, 20, c100, Torus_Regular, anchor='mm')
            w_katu = datatext(827.5, 480, 20, ckatu, Torus_Regular, anchor='mm')
            im = draw_text(im, w_katu)
            w_miss = datatext(910, 480, 20, cmiss, Torus_Regular, anchor='mm')
        else:
            # pfm_x = [622, 753, 884, 591, 655, 720, 786, 852, 917]
            w_acc = datatext(622, 420, 20, '{:.2f}%'.format(acc * 100), Torus_Regular, anchor='mm')
            w_maxcb = datatext(753, 420, 20, f'{format(maxcb, ",")}x', Torus_Regular, anchor='mm')
            w_pp = datatext(884, 420, 20, pp, Torus_Regular, anchor='mm')
            w_geki = datatext(591, 480, 20, cgeki, Torus_Regular, anchor='mm')
            im = draw_text(im, w_geki)
            w_300 = datatext(656, 480, 20, c300, Torus_Regular, anchor='mm')
            w_katu = datatext(720.5, 480, 20, ckatu, Torus_Regular, anchor='mm')
            im = draw_text(im, w_katu)
            w_100 = datatext(786, 480, 20, c100, Torus_Regular, anchor='mm')
            w_50 = datatext(852.5, 480, 20, c50, Torus_Regular, anchor='mm')
            im = draw_text(im, w_50)
            w_miss = datatext(917, 480, 20, cmiss, Torus_Regular, anchor='mm')
        im = draw_text(im, w_acc)
        im = draw_text(im, w_maxcb)
        im = draw_text(im, w_pp)
        im = draw_text(im, w_300)
        im = draw_text(im, w_100)
        im = draw_text(im, w_miss)

        outputimage_path = os.path.join(osufile, 'output', f'recent_{uid}.png')
        im.save(outputimage_path)
        msg = f'[CQ:image,file=file:///{outputimage_path}]'
    except Exception as e:
        return f'Error: {e}'
    return msg

async def best_pfm(id, mode, min, max, mods=False):
    info = await get_api_info('bp', id, mode)
    if isinstance(info, str):
        return info
    bp = []
    if mods:
        setmods = get_mods_num(mods)
        modslist = set_mod_list(info, setmods)
        if not modslist:
            return '没有在bp上查询到开启该mod的成绩'
        max = len(modslist)
        mods = ','.join(mods)
        bp.append(f"{id}'s Best Performance:\n{mode} {mods} BP {min} - {max}")
        msg = "".join(bp)
        for num in modslist:
            s = info[num]
            pp = s['pp']
            mapid = s['beatmap']['id']
            bp_msg = f'\nBP {num+1}  {pp}pp  id:{mapid}'
            bp.append(bp_msg)
            msg = "".join(bp)
    else:
        bp.append(f"{id}'s Best Performance:\n{mode} BP {min} - {max}")
        msg = "".join(bp)
        for num in range(min-1, max):
            s = info[num]
            pp = s['pp']
            mapid = s['beatmap']['id']
            bp_msg = f'\nBP {num+1}  {pp}pp  id:{mapid}'
            bp.append(bp_msg)
            msg = "".join(bp)
    return msg

async def map_info(mapid, mods):
    info = await get_api_info('map', mapid=mapid)
    if not info:
        return '未查询到该地图信息'
    if isinstance(info, str): 
        return info
    msg = ''
    mapinfo = []
    diff = info['difficulty_rating']
    mode = info['mode']
    status = info['status']
    total_len = info['total_length']
    version = info['version']
    bmapid = info['beatmapset_id']
    bpm = info['bpm']
    od = info['accuracy']
    ar = info['ar']
    cs = info['cs']
    hp = info['drain']
    bmap = info['beatmapset']
    artist = bmap['artist_unicode']
    title = bmap['title_unicode']
    creator = bmap['creator']
    source = bmap['source']
    cover = bmap['covers']['list@2x']
    music = bmap['preview_url']
    if source == None:
        source = 'Nothing'
    ranked_date = bmap['ranked_date']
    map_cb = info['max_combo']

    dirpath = await MapDownload(bmapid)
    version_osu = get_file(dirpath, mapid, version)
    if mode == 'osu':
        map_pp = calc_acc_pp(version_osu, mods)[5]
    else:
        map_pp = 'Std Only'

    map_len = list(divmod(int(total_len), 60))
    map_len[1] = map_len[1] if map_len[1] >= 10 else f'0{map_len[1]}'
    music_len = f'{map_len[0]}:{map_len[1]}'

    old_time = datetime.strptime(ranked_date.replace('+00:00', ''), '%Y-%m-%dT%H:%M:%S')
    new_time = (old_time + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')

    musicinfo = f'[CQ:record,file=https:{music}]'
    mapinfo.append(f'[CQ:image,file={cover}]\n')
    mapinfo.append(f'Query Map: {mapid} | Mode: {GMN[mode].capitalize()}\n')
    mapinfo.append(f'Title: {title}\n')
    mapinfo.append(f'Artist: {artist}\n')
    mapinfo.append(f'Source: {source}\n')
    mapinfo.append(f'Status: {status.capitalize()} | Song length: {music_len}\n')
    mapinfo.append(f'Version: {version} | Mapper: {creator}\n')
    mapinfo.append(f'Approved Time: {new_time}\n')
    mapinfo.append(f'Stars: {diff} | CS: {cs} | AR: {ar} | OD: {od} | HP: {hp} | BPM: {bpm}\n')
    mapinfo.append(f'Max Combo: {map_cb} | SS PP: {map_pp}')

    msg = ''.join(mapinfo)
    return musicinfo, msg

async def bindinfo(project, id, qid):
    esql = osusql()
    info = await get_api_info(project, id, GM[0])
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
    info = await get_api_info(project, id, mode)
    if not info:
        return '为查询到该玩家'
    elif isinstance(info, str):
        return info
    icon = info['avatar_url']
    header = info['cover_url']
    icon_t = await get_project_img('icon', icon, id, True)
    header_t = await get_project_img('header', header, id, True)
    if icon_t and header:
        return '头像和头图更新完毕'
    else:
        return '头像和头图更新失败'

async def get_map_bg(mapid):
    info = await get_api_info('map', mapid=mapid)
    if not info:
        return '未查询到该地图'
    elif isinstance(info, str):
        return info
    version = info['version']
    bmapid = info['beatmapset_id']
    dirpath = await MapDownload(bmapid)
    version_osu = get_file(dirpath, mapid, version)
    path = get_picture(version_osu)
    msg = f'[CQ:image,file=file:///{dirpath}/{path}]'
    return msg

async def user(id, update=False):
    esql = osusql()
    for mode in range(0, 4):
        if not update:
            new = esql.get_all_newinfo(id, mode)
            if new:
                continue
        info = await get_api_info('update', id, GM[mode])
        if info['statistics']['play_count'] != 0:
            username = info['username']
            play = info['statistics']
            count = play['total_hits']
            pc = play['play_count']
            g_ranked = play['global_rank']
            pp = play['pp']
            acc = round(play['hit_accuracy'], 2)
            c_ranked = play['country_rank']
            if update:
                esql.update_all_info(id, c_ranked, g_ranked, pp, acc, pc, count, mode)
            else:
                esql.insert_all_info(id, c_ranked, g_ranked, pp, acc, pc, count, mode)
        else:
            if update:
                esql.update_all_info(id, 0, 0, 0, 0, 0, 0, mode)
            else:
                esql.insert_all_info(id, 0, 0, 0, 0, 0, 0, mode)
        print(f'玩家:[{username}] {GM[mode]}模式 个人信息更新完毕')
