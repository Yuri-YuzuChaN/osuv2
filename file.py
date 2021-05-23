import aiohttp, os, re, zipfile, aiohttp

osufile = os.path.join(os.path.dirname(__file__), 'osufile')
mapfile = os.path.join(osufile, 'map')
iconfile = os.path.join(osufile, 'icon')
badges = os.path.join(osufile, 'badges')
coverfile = os.path.join(osufile, 'cover')

for item in ['badges', 'cover', 'icon', 'map', 'output']:
    RES = os.path.join(osufile, item)
    if not os.path.exists(RES):
        os.makedirs(RES)
        print(f'{item.capitalize()} Floder Created Successfully')

async def MapDownload(mapid, DL=False):
    # 判断是否存在该文件
    mapid = str(mapid)
    if not DL:
        for file in os.listdir(mapfile):
            if mapid in file:
                if os.path.exists(os.path.join(mapfile, file)):
                    return os.path.join(mapfile, file)
    url = f'https://txy1.sayobot.cn/beatmaps/download/novideo/{mapid}'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, allow_redirects=False) as re:
                sayo = re.headers['Location']
    except:
        print('Request Failed or Timeout')
        return
    if DL:
        filename = await get_osz(sayo, mapid, True)
        return os.path.join(mapfile, filename), filename
    filename = await get_osz(sayo, mapid)
    filepath = os.path.join(mapfile, filename)
    # 解压下载的osz文件
    myzip = zipfile.ZipFile(filepath)
    mystr = myzip.filename.split(".")
    myzip.extractall(mystr[0])
    myzip.close()
    end = ['mp3','wav','mp4','avi','mov','ogg','osb','flv']
    # 删除其余不需要的文件
    for root, dirs, files in os.walk(filepath[:-4], topdown=False):
        for name in files:
            for i in end:
                if name.endswith(i):
                    os.remove(os.path.join(root, name))
    # 删除下载osz文件
    os.remove(filepath)
    return filepath[:-4]

async def get_osz(sayo, mapid, DL=False):
    try:
        print('Start Downloading Map')
        async with aiohttp.ClientSession() as session:
            async with session.get(sayo) as req:
                filename = f'{mapid}.osz'
                if DL:
                    filename = req.content_disposition.filename
                chunk = await req.read()
                open(os.path.join(mapfile, filename), 'wb').write(chunk)
        print('Map Download Complete')
        return filename
    except:
        print('Map Download Failed')
        return

def get_file(path, mapid, version):
    for file in os.listdir(path):
        if '.osu' in file:
            with open(os.path.join(path, file), 'r', encoding='utf-8') as f:
                text = f.read()
            result = re.finditer(r'BeatmapID:(.+)', text)
            try:
                for i in result:
                    rmapid = i.groups()[0]
                if str(mapid) == rmapid:
                    filepath = os.path.join(path, file)
                    return filepath
            except:
                continue
    else:
        for file in os.listdir(path):
            if version in file:
                filepath = os.path.join(path, file)
                return filepath

def get_picture(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    result = re.finditer(r'\d,\d,\"(.+?)\"', text)
    for i in result:
        return i.groups()[0]

async def get_project_img(project, url, uid=0, update=False):
    uid = str(uid)
    if project == 'cover':
        name = f'{uid}_cover.png'
    elif project == 'icon':
        name = f'{uid}_icon.png'
    elif project == 'header':
        name = f'{uid}_headericon.png'
    elif project == 'badges':
        result = re.match(r'https://assets.ppy.sh/profile-badges/(.+)', url)
        name = result.group(1)
    if project == 'badges':
        path = os.path.join(badges, name)
    elif project == 'cover':
        path = os.path.join(coverfile, name)
    else:
        path = os.path.join(iconfile, name)
    if not update:
        if project == 'badges':
            lpath = badges
        else:
            lpath = iconfile
        for file in os.listdir(lpath):
            if name in file:
                return path
    try:
        if 'avatar-guest.png' in url:
            url = 'https://osu.ppy.sh/images/layout/avatar-guest.png'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as req:
                chunk = await req.read()
                open(path, 'wb').write(chunk)
        if update:
            return True
        return path
    except Exception as e:
        if project == 'cover':
            return os.path.join(osufile, 'work', 'mapbg.png')
        return e

def get_mode_img(mode, diff=None):
    if diff:
        if mode == 0:
            img = f'std_{diff}.png'
        elif mode == 1:
            img = f'taiko_{diff}.png'
        elif mode == 2:
            img = f'ctb_{diff}.png'
        else:
            img = f'mania_{diff}.png'
        return os.path.join(osufile, 'work', img)
    else:
        if mode == 0:
            img = 'pfm_std.png'
        elif mode == 1:
            img = 'pfm_taiko.png'
        elif mode == 2:
            img = 'pfm_ctb.png'
        else:
            img = 'pfm_mania.png'
        return os.path.join(osufile, img)
