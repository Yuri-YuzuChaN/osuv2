from .api import PPApi

class PPCalc:

    def __init__(self, mode: int, mapid: int) -> None:
        self.mapid: int = mapid
        self.mode: int = mode

    def __data__(self, mode: int, info: dict):
        self.pp = int(info['pp'])
        self.ifpp = int(info['ifpp'])
        self.sspp = int(info['sspp'])
        self.stars = float(f'{info["StarRating"]:.2f}')
        if mode == 0:
            self.aim = int(info['aim'])
            self.acc = int(info['accuracy'])
            self.speed = int(info['speed'])
            self.ar = float(f'{info["AR"]:.1f}')
            self.od = float(f'{info["OD"]:.1f}')

    async def if_pp(self, mods: list) -> int:
        info = await PPApi(self.mapid, self.mode, mods=mods, isPlay=False)
        self.__data__(self.mode, info)
        if self.mode == 0:
            return self.ifpp, self.stars, self.ar, self.od
        else:
            return self.ifpp, self.stars

    async def osu_pp(self, acc: float, combo: int, c300: int, c100: int, c50: int, miss: int, mods: list):
        info = await PPApi(self.mapid, 0, acc, combo, c300, c100, c50, miss=miss, mods=mods)
        self.__data__(self.mode, info)
        return self.pp, self.ifpp, self.sspp, self.aim, self.speed, self.acc, self.stars, self.ar, self.od

    async def taiko_pp(self, acc: float, combo: int, c300: int, c100: int, c50:int, miss: int, mods: list):
        info = await PPApi(self.mapid, 1, acc, combo, c300, c100, c50, miss=miss, mods=mods)
        self.__data__(self.mode, info)
        return self.pp, self.ifpp, self.stars

    async def catch_pp(self, acc: float, combo: int, c300: int, c100: int, c50: int, katu: int, miss: int, mods: list):
        info = await PPApi(self.mapid, 2, acc, combo, c300, c100, c50, katu=katu, miss=miss, mods=mods)
        self.__data__(self.mode, info)
        return self.pp, self.ifpp, self.stars

    async def mania_pp(self, acc: float, combo: int, c300: int, c100: int, c50: int, geki: int, katu: int, miss: int, score: int, mods: list):
        info = await PPApi(self.mapid, 3, acc, combo, c300, c100, c50, geki, katu, miss, score, mods)
        self.__data__(self.mode, info)
        return self.pp, self.ifpp, self.stars
