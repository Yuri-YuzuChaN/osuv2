from typing import Union, Type, List
from hoshino.config import SUPERUSERS
from nonebot import get_bot

import aiohttp, json, os, traceback
from . import *


API = 'https://osu.ppy.sh/api/v2'
SAYOAPI = 'https://api.sayobot.cn'
PPAPI = 'https://api.yuzuai.xyz/osu'

class OsuToken:

    def __init__(self) -> None:
        self.load()

    def load(self):
        self.token_json = os.path.join(PATH, 'token.json')
        self.token: dict = json.load(open(self.token_json, 'r', encoding='utf-8'))

    async def update_token(self) -> Union[str, bool]:
        bot = get_bot()
        user_id = SUPERUSERS[0]
        url = 'https://osu.ppy.sh/oauth/token'
        data = {
            'grant_type' : 'refresh_token',
            'client_id' : self.token['client_id'],
            'client_secret' : self.token['client_secret'],
            'refresh_token' : self.token['refresh_token']
        }
        try:
            async with aiohttp.request('POST', url, data=data) as req:
                if req.status != 200:
                    sv.logger.error(f'OAuth Certification Error: {req.status}')
                    await bot.send_private_msg(user_id=user_id, message=f'OAuth 认证失败 {req.status}')
                    return f'Error: API请求失败'
                newtoken = await req.json()
        except Exception as e:
            sv.logger.error(f'OAuth Certification Error: {e}')
            await bot.send_private_msg(user_id=user_id, message=f'OAuth 认证失败: {type(e)}')
            return f'Error: {type(e)}'

        self.token['access_token'] = newtoken['access_token']
        self.token['refresh_token'] = newtoken['refresh_token']

        try:
            with open(self.token_json, 'w', encoding='utf-8') as f:
                json.dump(self.token, f, ensure_ascii=False, indent=4)
        except Exception as e:
            traceback.print_exc()
            sv.logger.error(e)
        sv.logger.info('OAuth Certification Successful')
        await bot.send_private_msg(user_id=user_id, message='OAuth 认证令牌更新完毕')
        return True

    @property
    def access_token(self) -> str:
        '''返回 `access_token` '''
        return self.token['access_token']

token = OsuToken()

async def osu_api(project: str, id: Union[int, str] = 0, mode: str = 'osu', mapid: int = 0, mods: List[str] = [], isint: bool = False) -> Union[dict, bool]:
    try:
        if id and not isint:
            info = await user_info(f'{API}/users/{id}')
            if isinstance(info, str):
                return info
            else:
                id = info['id']
        if project == 'bind':
            url = f'{API}/users/{id}'
        elif project == 'info' or project == 'update':
            url = f'{API}/users/{id}/{mode}'
        elif project == 'recent':
            url = f'{API}/users/{id}/scores/{project}?mode={mode}&include_fails=1'
        elif project == 'passrecent' or project == 'tr':
            url = f'{API}/users/{id}/scores/recent?mode={mode}'
        elif project == 'score':
            mod = ''
            for m in mods:
                mod += f'&mods[]={m}'
            if mode != 'osu':
                url = f'{API}/beatmaps/{mapid}/scores/users/{id}?mode={mode}{mod}'
            else:
                url = f'{API}/beatmaps/{mapid}/scores/users/{id}?{mod}'
        elif project == 'bp' or project == 'pfm' or project == 'tbp':
            url = f'{API}/users/{id}/scores/best?mode={mode}&limit=100'
        elif project == 'map':
            url = f'{API}/beatmaps/{mapid}'
        else:
            raise 'Project Error'
        return await ApiInfo(project, url)
    except:
        return False

async def SayoApi(setid: int) -> Union[dict, bool]:
    try:
        url = f'{SAYOAPI}/v2/beatmapinfo?0={setid}'
        return await ApiInfo('mapinfo', url)
    except:
        return False

async def PPApi(mapid: int, mode: int, acc: float = 0, combo: int = 0, c300: int = 0, c100: int = 0, c50: int = 0,
            geki: int = 0, katu: int = 0, miss: int = 0, score: int = 1000000, mods: list = [], isPlay: bool = True) -> Union[dict, Type[Exception]]:
    try:
        if mode == 0:
            data = {
                'BeatmapID': mapid,
                'Mode': mode,
                'Accuracy': acc,
                'Combo': combo,
                'C300': c300,
                'C100': c100,
                'C50': c50,
                'Miss': miss,
                'Mods': ''.join(mods),
                'isPlay': str(isPlay)
            }
        elif mode == 1:
            data = {
                'BeatmapID': mapid,
                'Mode': mode,
                'Accuracy': acc,
                'Combo': combo,
                'C300': c300,
                'C100': c100,
                'C50': c50,
                'Miss': miss,
                'Mods': ''.join(mods),
                'isPlay': str(isPlay)
            }
        elif mode == 2:
            data = {
                'BeatmapID': mapid,
                'Mode': mode,
                'Accuracy': acc,
                'Combo': combo,
                'C300': c300,
                'C100': c100,
                'C50': c50,
                'Katu': katu,
                'Miss': miss,
                'Mods': ''.join(mods),
                'isPlay': str(isPlay)
            }
        elif mode == 3:
            data = {
                'BeatmapID': mapid,
                'Mode': mode,
                'Accuracy': acc,
                'Score': score,
                'C300': c300,
                'Geki': geki,
                'Katu': katu,
                'C100': c100, 
                'C50': c50,
                'Miss': miss,
                'Mods': ''.join(mods),
                'isPlay': str(isPlay)
            }
        else:
            raise 'mode Error'
        async with aiohttp.request('GET', PPAPI + '/PPCalc', params=data) as req:
            return await req.json()
    except Exception as e:
        sv.logger.error(traceback.print_exc())
        return f'Error: {type(e)}'

async def user_info(url: str) -> Union[dict, str]:
    try:
        header = {'Authorization' : f'Bearer {token.access_token}'}
        async with aiohttp.request('GET', url, headers=header) as req:
            if req.status == 401:
                await token.update_token()
                return await user_info(url)
            elif req.status == 404:
                return '未找到该玩家，请确认玩家ID'
            elif req.status == 200:
                return await req.json()
            else:
                return 'API请求失败，请联系管理员'
    except Exception as e:
        sv.logger.error(traceback.format_exc())
        return f'Error: {type(e)}'

async def ApiInfo(project: str, url: str) -> Union[dict, str]:
    try:
        if project == 'mapinfo' or project == 'PPCalc':
            headers = {'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
        else:
            headers = {'Authorization' : f'Bearer {token.access_token}'}
        async with aiohttp.request('GET', url, headers=headers) as req:
            if req.status == 401:
                sv.logger.info('OAuth 认证令牌过期，正在重新更新Token')
                result = await token.update_token()
                if isinstance(result, str):
                    return result
                return await ApiInfo(project, url)
            elif req.status == 404:
                if project == 'info' or project == 'bind':
                    return '未找到该玩家，请确认玩家ID'
                elif project == 'recent' or project == 'passrecent' or project == 'tr':
                    return '没有游玩记录'
                elif project == 'score':
                    return '未找到该地图成绩，请确认地图ID或模式'
                elif project == 'bp' or project == 'pfm' or project == 'tbp':
                    return '未找到该玩家BP'
                elif project == 'map':
                    return '未找到该地图，请确认地图ID'
                else:
                    return 'API请求失败，请联系管理员或稍后再尝试'
            if project == 'mapinfo':
                return await req.json(content_type='text/html', encoding='utf-8')
            else:
                return await req.json()
    except Exception as e:
        sv.logger.error(traceback.format_exc())
        return f'Error: {type(e)}'