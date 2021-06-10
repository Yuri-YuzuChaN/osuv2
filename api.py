import aiohttp, json, os, traceback, hoshino

api = 'https://osu.ppy.sh/api/v2'
sayoapi = 'https://api.sayobot.cn'
chimuapi = 'https://api.chimu.moe/cheesegull/search'
token_json = os.path.join(os.path.dirname(__file__), 'token.json')

def get_token_json():
    with open(token_json, encoding='utf-8') as f:
        i = json.load(f)
        client_id = i["client_id"]
        client_secret = i['client_secret']
        access_token = i['access_token']
        refresh_token = i['refresh_token']
    return access_token, refresh_token, client_id, client_secret

async def get_api_info(project, id=0, mode='osu', mapid=0):
    try:
        if not str(id).isdigit():
            url = f'{api}/users/{id}'
            info = await return_info(project, url)
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
            url = f'{api}/users/{id}/scores/best?mode={mode}&limit=50'
        elif project == 'map':
            url = f'{api}/beatmaps/{mapid}'
        else:
            hoshino.logger.info('Project Error')
            return
        return await return_info(project, url)
    except:
        return False

async def get_sayoapi_info(project, mode=1, status=1, keyword=None, setid=0):
    try:
        if project == 'search':
            data = {
                'class' : status,
                'cmd' : 'beatmaplist',
                'keyword' : keyword,
                'limit' : 10,
                'mode' : mode,
                'offset' : 0,
                'type' : 'search'
            }
            url = f'{sayoapi}/?post'
            data = json.dumps(data)
        elif project == 'mapinfo':
            url = f'{sayoapi}/v2/beatmapinfo?0={setid}'
            data = None
        else:
            hoshino.logger.info('Project Error')
            return
        return await return_info(project, url, data)
    except:
        return False

async def get_chimuapi_info(mode, status, keyword):
    try:
        url = f'{chimuapi}?query={keyword}&amount=10&status={status}&mode={mode}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as req:
                if req.status != 200:
                    return 'API请求失败，请联系管理员或稍后再尝试'
                return await req.json()
    except:
        return False

async def return_info(project, url, data=None):
    try:
        if not data:
            if project != 'mapinfo':
                headers = {'Authorization' : f'Bearer {get_token_json()[0]}'}
            else:
                headers = {'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as req:
                    if req.status != 200:
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
                    if project != 'mapinfo':
                        return await req.json()
                    return await req.json(content_type='text/html', encoding='utf-8')
        else:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data) as req:
                    if req.status != 200:
                        return 'API请求失败，请联系管理员或稍后再尝试'
                    return await req.json()
    except Exception as e:
        hoshino.logger.error(e)
        return e

async def get_access_token():
    token = get_token_json()
    url = 'https://osu.ppy.sh/oauth/token'
    data = {
        'grant_type' : 'refresh_token',
        'client_id' : token[2],
        'client_secret' : token[3],
        'refresh_token' : token[1]
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as req:
                if req.status != 200:
                    return 'OAuth 认证失败'
                newtoken = await req.json()
    except Exception as e:
        hoshino.logger.error(f'OAuth Certification Error: {e}')
        return 'OAuth 认证失败'
    new_json = {
        'client_id' : token[2],
        'client_secret' : token[3],
        'access_token' : newtoken['access_token'],
        'refresh_token' : newtoken['refresh_token']
    }
    try:
        with open(token_json, 'w', encoding='utf-8') as f:
            json.dump(new_json, f, ensure_ascii=False, indent=2)
    except:
        traceback.print_exc()
    hoshino.logger.info('OAuth Certification Successful')
    return 'OAuth 认证令牌更新完毕'
