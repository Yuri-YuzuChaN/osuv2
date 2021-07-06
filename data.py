from .mods import modsnum, setmodslist
import os

class UserInfo:
    '''
    个人信息
    '''

    def __init__(self, info: dict):
        '''
        返回 `info` 数据
        '''
        self.icon: str = info['avatar_url']
        self.country_code: str = info['country_code']
        self.uid: int = info['id']
        self.user_status: bool = info['is_online']
        self.supporter: bool = info['is_supporter']
        self.username: str = info['username']
        self.cover_url: str = info['cover_url']
        self.badges: list = info['badges']
        self.play: dict = info['statistics']
        self.level: dict = self.play['level']
        self.current: int = self.level['current']
        self.progress: int = self.level['progress']
        self.grank: int = self.play['global_rank'] if self.play['global_rank'] else 0
        self.pp: float = self.play['pp']
        self.r_score: int = self.play['ranked_score']
        self.acc: float = self.play['hit_accuracy']
        self.play_count: int = self.play['play_count']
        self.play_time: int = self.play['play_time']
        self.play_hits: int = self.play['total_hits']
        self.t_score: int = self.play['total_score']
        self.count: int = self.play['total_hits']
        self.g_counts: dict = self.play['grade_counts']
        self.gc: list = self.g_counts['ssh'], self.g_counts['ss'], self.g_counts['sh'], self.g_counts['s'], self.g_counts['a']
        self.crank: int = self.play['country_rank'] if self.play['country_rank'] else 0

class ScoreInfo:
    '''
    成绩信息
    '''

    info = None

    def __init__(self, info: dict):
        '''
        返回 `score` 数据
        '''
        self.info = info

    def __AllScore(self, info: dict):
        '''
        返回 `score` 数据
        '''
        self.uid: int = info['user_id']
        self.acc: float = info['accuracy']
        self.mods: list = info['mods']
        self.score: int = info['score']
        self.maxcb: int = info['max_combo']
        self.count: dict = info['statistics']
        self.mode: int = info['mode_int']
        self.c50: int = self.count['count_50']
        self.c100: int = self.count['count_100']
        self.c300: int = self.count['count_300']
        self.cgeki: int = self.count['count_geki']
        self.ckatu: int = self.count['count_katu']
        self.cmiss: int = self.count['count_miss']
        self.rank: int = info['rank']
        self.date: str = info['created_at']
        self.pp: float = info['pp'] if info['pp'] else -1
        self.setid: int = info['beatmap']['beatmapset_id']
        self.mapid: int = info['beatmap']['id']
        self.version: str = info['beatmap']['version']
        self.map_status: str = info['beatmap']['status']
        self.user: str = info['user']
        self.icon_url: str = self.user['avatar_url']
        self.country_code: str = self.user['country_code']
        self.user_status: bool = self.user['is_online']
        self.supporter: bool = self.user['is_supporter']
        self.username: str = self.user['username']

    def __SetMods(self, mods: list, min: int = 0):
        '''
        计算开启 `mod` 的数字和
        '''
        setmods = modsnum(mods)
        self.modslist = setmodslist(self.info, setmods)
        if min:
            self.modsbool = len(self.modslist) < min

    def RecentScore(self) -> dict:
        '''
        返回 `recent` 数据
        '''
        return self.__AllScore(self.info[0])

    def BPScore(self, bp: int = 0, mods: list = []) -> dict:
        '''
        返回 `BP` 数据
        '''
        if bp:
            if mods:
                self.__SetMods(mods)
                if self.modslist:
                    self.info = self.info[self.modslist[bp - 1]]
                else:
                    return
            else:
                self.info = self.info[bp - 1]

        return self.__AllScore(self.info)

    def MapScore(self) -> dict:
        '''
        返回 `Score` 成绩数据
        '''
        self.grank: int = self.info['position']
        self.info: dict = self.info['score']
        self.headericon: str = self.info['user']['cover']['url']

        return self.__AllScore(self.info)

    def BestBPScore(self, min: int, max: int, mods: list = []) -> dict:
        '''
        返回 `BestBP` 成绩指定列表
        '''
        self.bpList = []
        if mods:
            self.__SetMods(mods, min)
            if self.modslist:
                self.bpList = self.modslist[min-1:max]
        else:
            self.bpList = range(min-1, max)
        
        return self.bpList

    def BestScore(self, bp: int) -> dict:
        '''
        返回 `BestBP` 成绩数据
        '''
        self.map: dict = self.info[bp]['beatmapset']
        self.artist: str = self.map['artist_unicode'] if self.map['artist_unicode'] else self.map['artist']
        self.title: str = self.map['title_unicode'] if self.map['title_unicode'] else self.map['title']
        
        return self.__AllScore(self.info[bp])

class Beatmapset:
    '''
    地图信息
    '''

    def __init__(self, info: dict):
        '''
        返回地图数据
        '''
        self.mode: int = info['mode_int']
        self.status: str = info['status']
        self.total_len: int = info['total_length']
        self.version: str = info['version']
        self.diff: float = info['difficulty_rating']
        self.od: float = info['accuracy']
        self.ar: float = info['ar']
        self.cs: float = info['cs']
        self.hp: float = info['drain']
        self.mapdiff: list = [self.cs, self.hp, self.od, self.ar, self.diff]
        self.bpm: float = info['bpm']
        self.c_circles: int = info['count_circles']
        self.c_sliders : int = info['count_sliders']
        self.setid: int = info['beatmapset_id']
        self.map: dict = info['beatmapset']
        self.maxcb: int = info['max_combo'] if self.mode != 3 else 0
        self.artist: str = self.map['artist_unicode'] if self.map['artist_unicode'] else self.map['artist']
        self.title: str = self.map['title_unicode'] if self.map['title_unicode'] else self.map['title']
        self.mapper: str = self.map['creator']
        self.uid: int = self.map['user_id']
        self.source: str = self.map['source'] if self.map['source'] else 'Nothing'
        self.cover: str = self.map['covers']['list@2x']
        self.music: str = self.map['preview_url']
        self.ranked_date: str = self.map['ranked_date']

class SayoInfo:

    def __init__(self, info: dict):
        '''
        返回 SayoApi `map` 数据
        '''
        self.setid: int = info['sid']
        self.title: str = info['titleU'] if info['titleU'] else info['title']
        self.artist: str = info['artistU'] if info['artistU'] else info['artist']
        self.mapper: str = info['creator']
    
    def map(self, info: dict):
        self.apptime = info['approved_date']
        self.source: str = info['source'] if info['source'] else 'Nothing'
        self.bpm: float = info['bpm']
        self.gmap: dict = info['bid_data']
        self.songlen: int = self.gmap[0]['length']
    
    def mapinfo(self, info: dict):
        self.diff: list = [info['CS'], info['HP'], info['OD'], info['AR']]
        self.bid: int = info['bid']
        self.maxcb: str = info['maxcombo']
        self.mode: int = info['mode']
        self.star: float = round(info['star'], 2)
        self.version: str = info['version']

class ChumiInfo(SayoInfo):

    def __init__(self, info: dict):
        '''
        返回 ChumiApi `map` 数据
        '''
        self.setid: int = info['SetID']
        self.title: str  = info['Title']
        self.artist: str  = info['Artist']
        self.mapper: str  = info['Creator']