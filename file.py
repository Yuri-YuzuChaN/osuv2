import aiohttp, os, re, zipfile, aiohttp

osupath = os.path.dirname(__file__)
osufile = f'{osupath}/osufile/'
mapfile = f'{osufile}map/'
iconfile = f'{osufile}icon/'

async def MapDownload(mapid):
    # 判断是否存在该文件
    mapid = str(mapid)
    for file in os.listdir(mapfile):
        if mapid in file:
            if os.path.exists(f'{mapfile}{file}'):
                return f'{mapfile}{file}'
        continue
    else:
        url = f'https://txy1.sayobot.cn/beatmaps/download/novideo/{mapid}'
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, allow_redirects = False) as re:
                    sayo = re.headers['Location']
        except:
            print('Request Failed or Timeout')
            return
        filename = await get_osz(sayo, mapid)
        filepath = mapfile + filename
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
        
async def get_osz(sayo, mapid):
    try:
        print('Start Downloading Map')
        async with aiohttp.ClientSession() as session:
            async with session.get(sayo) as req:
                filename = f'{mapid}.osz'
                chunk = await req.read()
                open(f'{mapfile}{filename}', 'wb').write(chunk)
        print('Map Download Complete')
        return filename
    except:
        print('Map Download Failed')
        return 

def get_file(path, mapid, version):
    for file in os.listdir(path):
        if '.osu' in file:
            with open(f'{path}/{file}', 'r', encoding='utf-8') as f:
                text = f.read()
            result = re.finditer(r'BeatmapID:(.+)', text)
            try:
                for i in result:
                    rmapid = i.groups()[0]
                if str(mapid) == rmapid:
                    filepath = f'{path}/{file}'
                    return filepath
            except:
                continue
    else:
        for file in os.listdir(path):
            if version in file:
                filepath = f'{path}/{file}'
                return filepath

def get_picture(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    result = re.finditer(r'\d,\d,\"(.+?)\"', text)
    for i in result:
        return i.groups()[0]

async def get_project_img(project, url, uid, update=False):
    uid = str(uid)
    if project == 'cover':
        name = f'{uid}_cover.png'
    elif project == 'icon':
        name = f'{uid}_icon.png'
    elif project == 'header':
        name = f'{uid}_headericon.png'
    if not update:
        for file in os.listdir(iconfile):
            if name in file:
                return iconfile + name
    try:
        if 'avatar-guest.png' in url:
            url = 'https://osu.ppy.sh/images/layout/avatar-guest.png'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as req:
                chunk = await req.read()
                open(iconfile + name, 'wb').write(chunk)
        if update:
            return True
        return iconfile + name
    except Exception as e:
        return e

def get_mode_img(mode, *diff):
    if diff:
        if mode == 0:
            img = f'std_{diff[0]}.png'
        elif mode == 1:
            img = f'taiko_{diff[0]}.png'
        elif mode == 2:
            img = f'ctb_{diff[0]}.png'
        else:
            img = f'mania_{diff[0]}.png'
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
        return os.path.join(osupath, 'osufile', img)
