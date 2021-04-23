import aiohttp, json, os, traceback

api = 'https://osu.ppy.sh/api/v2'
token_json = os.path.join(os.path.dirname(__file__), 'token.json')

def get_token_json():
    with open(token_json, encoding='utf-8') as f:
        i = json.load(f)
        client_id = i["client_id"]
        client_secret = i['client_secret']
        access_token = i['access_token']
        refresh_token = i['refresh_token']
    return access_token, refresh_token, client_id, client_secret

async def get_api_info(project, id=0, mode='osu', **kargs):
    try:
        if not str(id).isdigit():
            url = f'{api}/users/{id}'
            info = await return_info(url)
            id = info['id']
        if project == 'info' or project == 'bind' or project == 'update':
            url = f'{api}/users/{id}/{mode}'
        elif project == 'recent':
            url = f'{api}/users/{id}/scores/{project}?include_fails=1'
        elif project == 'score':
            if mode != 'osu':
                url = f'{api}/beatmaps/{kargs["mapid"]}/scores/users/{id}?mode={mode}'
            else:
                url = f'{api}/beatmaps/{kargs["mapid"]}/scores/users/{id}'
        elif project == 'bp':
            url = f'{api}/users/{id}/scores/best?mode={mode}&limit=50'
        elif project == 'map':
            url = f'{api}/beatmaps/{kargs["mapid"]}'
        else:
            print('Project Error')
            return
        return await return_info(url)
    except:
        return False

async def return_info(url):
    try:
        statue_code = True
        while statue_code:
            headers = {'Authorization' : f'Bearer {get_token_json()[0]}'}
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as req:
                    if req.status != 200:
                        if req.status == 404:
                            return '请确认查询的地图模式与BOT默认查询模式一致，可以在指令添加查询模式'
                        return 'API请求失败，请联系管理员或稍后再尝试'
                    return await req.json()
    except:
        return 'API请求失败，请联系管理员或稍后再尝试'

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
                    return 'Oauth 认证失败'
                newtoken = await req.json()
    except:
        return 'Oauth 认证失败'
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
    return 'Oauth 认证令牌更新完毕'
    