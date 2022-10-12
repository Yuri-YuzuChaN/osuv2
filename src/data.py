
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
        self.cover: str = self.map['covers']['cover@2x']
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