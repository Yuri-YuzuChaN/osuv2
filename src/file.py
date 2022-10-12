import aiohttp, os, re, zipfile, shutil, aiofiles
from io import BytesIO, TextIOWrapper
from typing import Union, Tuple

from . import *

async def MapDownload(setid: Union[str, int], DL: bool = False) -> Union[str, Tuple[str, str]]:
    # 判断是否存在该文件
    setid = str(setid)
    if not DL:
        for file in os.listdir(os.path.join(FILEPATH, 'map')):
            if setid == file:
                if os.path.exists(os.path.join(FILEPATH, 'map', file)):
                    return os.path.join(FILEPATH, 'map', file)
    url = f'https://txy1.sayobot.cn/beatmaps/download/novideo/{setid}'
    try:
        async with aiohttp.request('GET', url, allow_redirects=False) as req:
            sayo = req.headers['Location']
    except:
        sv.logger.error('Request Failed or Timeout')
        return
    if DL:
        filename = await osz_file_download(sayo, setid, True)
        return os.path.join(FILEPATH, 'map', filename), filename
    filename = await osz_file_download(sayo, setid)
    filepath = os.path.join(FILEPATH, 'map', filename)
    # 解压下载的osz文件
    myzip = zipfile.ZipFile(filepath)
    mystr = myzip.filename.split(".")
    myzip.extractall(mystr[0])
    myzip.close()
    #删除文件
    await remove_file(filepath[:-4])
    os.remove(filepath)
    return filepath[:-4]

async def osz_file_download(sayo: str, setid: int, DL: bool = False) -> str:
    try:
        async with aiohttp.request('GET', sayo) as req:
            osufilename = req.content_disposition.filename
            sv.logger.info(f'Start Downloading Map: {osufilename}')
            filename = f'{setid}.osz' if not DL else osufilename
            chunk = await req.read()
            async with aiofiles.open(os.path.join(FILEPATH, 'map', filename), 'wb') as f:
                await f.write(chunk)
        sv.logger.info(f'Map: <{osufilename}> Download Complete')
        return filename
    except Exception as e:
        sv.logger.error(f'Map: <{setid}> Download Failed Error:{e}')
        return

async def osu_file_download(mapid: int) -> bytes:
    try:
        async with aiohttp.request('GET', f'https://osu.ppy.sh/osu/{mapid}') as req:
            filename = req.content_disposition.filename
            sv.logger.info(f'Start Downloading .osu File: {filename}')
            osu = await req.read()
        sv.logger.info(f'.osu File: <{filename}> Download Complete')
        return osu
    except Exception as e:
        sv.logger.error(f'.osu File: <{mapid}> Download Failed! Error: {e}')
        return

async def get_image(url: str) -> Union[BytesIO, Exception]:
    try:
        if 'avatar-guest.png' in url:
            url = 'https://osu.ppy.sh/images/layout/avatar-guest.png'
        async with aiohttp.request('GET', url) as req:
            if req.status == 403:
                return os.path.join(FILEPATH, 'work', 'mapbg.png')
            data = await req.read()
        return BytesIO(data)
    except Exception as e:
        sv.logger.error(f'Image Failed: {e}')
        return e

async def remove_file(path: str) -> bool:
    bg_list = []
    for file in os.listdir(path):
        if '.osu' in file:
            bg = await re_map(os.path.join(path, file))
            if bg not in bg_list:
                bg_list.append(bg)
    
    for root, dir, files in os.walk(path, topdown=False):
        for name in files:
            if name not in bg_list:
                os.remove(os.path.join(root, name))
        for dirname in dir:
            shutil.rmtree(os.path.join(root, dirname))

    return True

async def re_map(file: Union[str, TextIOWrapper]) -> str:
    if isinstance(file, TextIOWrapper):
        text = file.read()
    else:
        async with aiofiles.open(file, 'r', encoding='utf-8') as f:
            text = await f.read()
    res = re.search(r'\d,\d,\"(.+)\"', text)
    bg = 'mapbg.png' if not res else res.group(1).strip()
    return bg