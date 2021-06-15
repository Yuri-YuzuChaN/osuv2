import aiohttp, os, re, zipfile, aiohttp, shutil, hoshino

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

async def MapDownload(setid, DL=False):
    # 判断是否存在该文件
    setid = str(setid)
    if not DL:
        for file in os.listdir(mapfile):
            if setid == file:
                if os.path.exists(os.path.join(mapfile, file)):
                    return os.path.join(mapfile, file)
    url = f'https://txy1.sayobot.cn/beatmaps/download/novideo/{setid}'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, allow_redirects=False) as req:
                sayo = req.headers['Location']
    except:
        hoshino.logger.error('Request Failed or Timeout')
        return
    if DL:
        filename = await get_osz(sayo, setid, True)
        return os.path.join(mapfile, filename), filename
    filename = await get_osz(sayo, setid)
    filepath = os.path.join(mapfile, filename)
    # 解压下载的osz文件
    myzip = zipfile.ZipFile(filepath)
    mystr = myzip.filename.split(".")
    myzip.extractall(mystr[0])
    myzip.close()
    #删除文件
    remove_file(filepath[:-4])
    os.remove(filepath)
    return filepath[:-4]

async def get_osz(sayo, setid, DL=False):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(sayo) as req:
                osufilename = req.content_disposition.filename
                hoshino.logger.info(f'Start Downloading Map: {osufilename}')
                filename = f'{setid}.osz' if not DL else osufilename
                chunk = await req.read()
                open(os.path.join(mapfile, filename), 'wb').write(chunk)
        hoshino.logger.info(f'Map: <{osufilename}> Download Complete')
        return filename
    except:
        hoshino.logger.error(f'Map: <{setid}> Download Failed')
        return

def remove_file(path):
    s = []
    for file in os.listdir(path):
        if '.osu' in file:
            bg = get_pic_music('pic', os.path.join(path, file))
            if bg not in s:
                s.append(bg)
            music = get_pic_music('music', os.path.join(path, file))
            if music not in s:
                s.append(music)
            s.append(file)

    for root, dir, files in os.walk(path, topdown=False):
        for name in files:
            if name not in s:
                os.remove(os.path.join(root, name))
        for dirname in dir:
            shutil.rmtree(os.path.join(root, dirname))
    
    return True

def get_file(path, mapid, version):
    for file in os.listdir(path):
        if '.osu' in file:
            with open(os.path.join(path, file), 'r', encoding='utf-8') as f:
                text = f.read()
            result = re.search(r'BeatmapID:(.+)', text)
            if result:
                rmapid = result.group(1)
                if str(mapid) == rmapid:
                    filepath = os.path.join(path, file)
                    return filepath
    for file in os.listdir(path):
        if version in file:
            filepath = os.path.join(path, file)
            return filepath

def get_pic_music(project, path):
    if project == 'pic':
        sre = r'\d,\d,\"(.+)\"'
    elif project == 'music':
        sre = r'AudioFilename:(.+)'
    else:
        raise 'project error'
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    result = re.search(sre, text)
    return result.group(1).strip()

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
    else:
        raise 'project error'
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
                if req.status == 403:
                    return os.path.join(osufile, 'work', 'mapbg.png')
                chunk = await req.read()
                open(path, 'wb').write(chunk)
        if update:
            return True
        return path
    except Exception as e:
        hoshino.logger.error(f'Image Failed: {e}')
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
