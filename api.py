from typing import Union, Type
import aiohttp, json, os, traceback
from nonebot import get_bot
from hoshino.log import new_logger
from hoshino.config import SUPERUSERS

api = 'https://osu.ppy.sh/api/v2'
sayoapi = 'https://api.sayobot.cn'
ppcalcapi = 'http://106.53.138.218:6321/api/osu'

logger = new_logger('osuv2_api')

class osutoken:

    def __init__(self) -> None:
        self.load()

    def load(self):
        self.token_json = os.path.join(os.path.dirname(__file__), 'token.json')
        self.token: dict = json.load(open(self.token_json, 'r', encoding='utf-8'))

    async def update_token(self) -> Union[str, bool]:
        bot = get_bot()
        url = 'https://osu.ppy.sh/oauth/token'
        data = {
            'grant_type' : 'refresh_token',
            'client_id' : self.token['client_id'],
            'client_secret' : self.token['client_secret'],
            'refresh_token' : self.token['refresh_token']
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data) as req:
                    if req.status != 200:
                        logger.error(f'OAuth Certification Error: {req.status}')
                        await bot.send_private_msg(user_id=SUPERUSERS[0], message=f'OAuth 认证失败 {req.status}，请尝试手动更新')
                        return 'Error: API请求失败'
                    newtoken = await req.json()
        except Exception as e:
            logger.error(f'OAuth Certification Error: {e}')
            await bot.send_private_msg(user_id=SUPERUSERS[0], message=f'OAuth 认证失败: {type(e)}，请尝试手动更新')
            return 'Error: API请求失败'

        self.token['access_token'] = newtoken['access_token']
        self.token['refresh_token'] = newtoken['refresh_token']

        try:
            with open(self.token_json, 'w', encoding='utf-8') as f:
                json.dump(self.token, f, ensure_ascii=False, indent=4)
        except Exception as e:
            traceback.print_exc()
            logger.error(e)
        logger.info('OAuth Certification Successful')
        await bot.send_private_msg(user_id=SUPERUSERS[0], message='OAuth 认证令牌更新完毕')
        return True
    
    @property
    def accesstoken(self) -> str:
        '''返回 `access_token` '''
        return self.token['access_token']

token = osutoken()

async def OsuApi(project: str, id: Union[int, str] = 0, mode: str = 'osu', mapid: int = 0, isint: bool = False) -> Union[dict, bool]:
    try:
        if id:
            if not isint:
                info = await User(f'{api}/users/{id}')
                if isinstance(info, str):
                    return info
                else:
                    id = info['id']
        if project == 'info' or project == 'bind' or project == 'update':
            url = f'{api}/users/{id}/{mode}'
        elif project == 'recent':
            url = f'{api}/users/{id}/scores/{project}?mode={mode}&include_fails=1'
        elif project == 'score':
            if mode != 'osu':
                url = f'{api}/beatmaps/{mapid}/scores/users/{id}?mode={mode}'
            else:
                url = f'{api}/beatmaps/{mapid}/scores/users/{id}'
        elif project == 'bp':
            url = f'{api}/users/{id}/scores/best?mode={mode}&limit=100'
        elif project == 'map':
            url = f'{api}/beatmaps/{mapid}'
        else:
            raise 'Project Error'
        return await ApiInfo(project, url)
    except:
        return False

async def SayoApi(setid: int) -> Union[dict, bool]:
    try:
        url = f'{sayoapi}/v2/beatmapinfo?0={setid}'
        return await ApiInfo('mapinfo', url)
    except:
        return False

async def PPApi(mode: int, mapid: int, acc: float = 0, combo: int = 0, good: int = 0, bad: int = 0,
                miss: int = 0, score: int = 1000000, mods: list = []) -> Union[dict, Type[Exception]]:
    try:
        if mode == 0:
            data = {
                'mode': mode,
                'map': mapid,
                'accuracy': acc,
                'combo': combo,
                'good': good,
                'bad': bad,
                'miss': miss,
                'mods': mods
            }
        elif mode == 1:
            data = {
                'mode': mode,
                'map': mapid,
                'accuracy': acc,
                'combo': combo,
                'good': good,
                'miss': miss,
                'mods': mods
            }
        elif mode == 2:
            data = {
                'mode': mode,
                'map': mapid,
                'accuracy': acc,
                'combo': combo,
                'miss': miss,
                'mods': mods
            }
        elif mode == 3:
            data = {
                'mode': mode,
                'map': mapid,
                'score': score,
                'mods': mods
            }
        else:
            raise 'mode Error'
        async with aiohttp.ClientSession() as session:
            async with session.post(ppcalcapi, json=data) as req:
                return await req.json()
    except Exception as e:
        logger.error(traceback.print_exc())
        return f'Error: {type(e)}'

async def User(url: str) -> Union[dict, str]:
    try:
        header = {'Authorization' : f'Bearer {token.accesstoken}'}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=header) as req:
                if req.status == 401:
                    await token.update_token()
                    return await User(url)
                elif req.status == 404:
                    return '未找到该玩家，请确认玩家ID'
                elif req.status == 200:
                    return await req.json()
                else:
                    return 'API请求失败，请联系管理员'
    except Exception as e:
        logger.error(traceback.print_exc())
        return f'Error: {type(e)}'

async def ApiInfo(project: str, url: str) -> Union[dict, str, Type[Exception]]:
    try:
        if project == 'mapinfo' or project == 'PPCalc':
            headers = {'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
        else:
            headers = {'Authorization' : f'Bearer {token.accesstoken}'}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as req:
                if req.status == 401:
                    logger.info('OAuth 认证令牌过期，正在重新更新Token')
                    result = await token.update_token()
                    if isinstance(result, str):
                        return result
                    return await ApiInfo(project, url)
                elif req.status == 404:
                    if project == 'info' or project == 'bind':
                        return '未找到该玩家，请确认玩家ID'
                    elif project == 'recent':
                        return '未找到该玩家，请确认玩家ID'
                    elif project == 'score':
                        return '未找到该地图成绩，请确认地图ID或模式'
                    elif project == 'bp':
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
        logger.error(traceback.print_exc())
        return f'Error: {type(e)}'