from typing import Any, List, Mapping, Optional, Union

from aiohttp import ClientResponse, ClientSession
from oauthlib.oauth2 import BackendApplicationClient, OAuth2Error, TokenExpiredError
from requests_oauthlib import OAuth2Session

from .. import *
from .Model import *


class OAuth(OAuth2Session):

    async def requestAsync(self,
                           method: str,
                           url: str,
                           session: ClientSession,
                           *,
                           headers: Mapping[str, str] = None,
                           params: Mapping[str, str] = None,
                           data: Mapping[str, str] = None
                           ) -> ClientResponse:

        for hook in self.compliance_hook['protected_request']:
            url, headers, data = hook(url, headers, data)

        url, headers, data = self._client.add_token(url, method, data, headers)

        return await session.request(method, url, headers=headers, params=params, data=data)


class OsuAPI:

    OsuAPIv2 = 'https://osu.ppy.sh/api/v2'
    TokenUrl = 'https://osu.ppy.sh/oauth/token'
    OAuthUrl = 'https://osu.ppy.sh/authorize'
    OsuPPAPI = 'https://api.yuzuai.xyz/osu'
    SayoAPI = 'https://api.sayobot.cn'

    def __init__(self,
                 client_id: int,
                 client_secret: str,
                 *,
                 refresh_token: Optional[str] = None
                 ) -> None:

        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.session = self._new_session()

    def _new_session(self) -> OAuth:
        client = BackendApplicationClient(self.client_id, scope=['public'])
        session = OAuth(client=client)
        token = session.fetch_token(
            self.TokenUrl, client_secret=self.client_secret)
        self.access_token = token['access_token']
        return session

    async def _request(self, method: str, url: str, params: Mapping[str, str] = None):
        """OsuAPIv2 HTTP 请求"""
        client_session = ClientSession()

        async def create_request() -> ClientResponse:
            return await self.session.requestAsync(method, url, client_session, params=params)

        async def reauthenticate_retry():
            self.session = self._new_session()
            return await create_request()

        try:
            res = await create_request()
        except TokenExpiredError:
            res = await reauthenticate_retry()
        except OAuth2Error as e:
            if e.description != "The refresh token is invalid.":
                raise
            res = await reauthenticate_retry()

        data = await res.json()

        if data == {"authentication": "basic"}:
            res = await reauthenticate_retry()
            data = await res.json()

        await client_session.close()

        return data
    
    async def _totalrequest(self, method: str, url: str, *, content_type: str = 'application/json', **kwargs):
        """
        通用 HTTP 请求
        """
        session = ClientSession()
        try:
            res = await session.request(method, url, **kwargs)
        except:
            pass
        data = await res.json(encoding='utf8', content_type=content_type)
        await session.close()
        return data
    

    async def user(self, user_id: Union[str, int], *, mode: Optional[str] = None):
        """获取用户信息"""
        return await self._request('GET', self.OsuAPIv2 + f'/users/{user_id}/{mode if mode else ""}')

    
    async def _get_user(self, user_id: str) -> int:
        data = await self.user(user_id)
        return data['id']
    

    async def user_recent(self, user_id: Union[str, int], *, mode: Optional[str] = None, include_fails: Optional[int] = None):
        """获取用户最近游玩成绩"""
        if isinstance(user_id, str) and user_id.isdigit():
            user_id = await self._get_user(user_id)
        params = {}
        if mode:
            params['mode'] = mode
        if include_fails:
            params['include_fails'] = include_fails
        return await self._request('GET', self.OsuAPIv2 + f'/users/{user_id}/scores/recent', params)


    async def user_scores(self, user_id: Union[str, int], mapid: int, *, mode: Optional[str] = None, mods: Optional[List[str]] = None):
        """获取用户游玩指定地图的最好成绩"""
        if isinstance(user_id, str) and not user_id.isdigit():
            user_id = await self._get_user(user_id)
        params = {}
        if mode:
            params['mode'] = mode
        if mods:
            params['mods[]'] = mods
        return await self._request('GET', self.OsuAPIv2 + f'/beatmaps/{mapid}/scores/users/{user_id}', params)


    async def user_scores_all(self, user_id: Union[str, int], mapid: int, *, mode: Optional[str] = None):
        """获取用户游玩指定地图的所有成绩"""
        if isinstance(user_id, str) and user_id.isdigit():
            user_id = await self._get_user(user_id)
        params = {}
        if mode:
            params['mode'] = mode
        return await self._request('GET', self.OsuAPIv2 + f'/beatmaps/{mapid}/scores/users/{user_id}/all', params)


    async def user_scores_best(self, user_id: Union[str, int], *, mode: Optional[str] = None, limit: Optional[int] = None):
        """获取用户的最好成绩排行榜"""
        if isinstance(user_id, str) and user_id.isdigit():
            user_id = await self._get_user(user_id)
        params = {}
        if mode:
            params['mode'] = mode
        if limit:
            params['limit'] = limit
        return await self._request('GET', self.OsuAPIv2 + f'/users/{user_id}/scores/best', params)
    
    
    async def beatmap(self, mapid: int):
        """获取指定地图信息"""
        return await self._request('GET', self.OsuAPIv2 + f'/beatmaps/{mapid}')
    
    
    async def sayomap(self, beatmapsetid: int):
        """获取 SayoAPI 的地图信息"""
        return await self._totalrequest('GET', self.SayoAPI + f'/v2/beatmapinfo', params={'0': beatmapsetid}, content_type='text/html')
    
    
    async def pp(self, params: Mapping[str, Any]):
        """计算 pp"""
        return await self._totalrequest('GET', self.OsuPPAPI + '/PPCalc', params=params)
    

osuApi = OsuAPI(client_id, client_secret)
