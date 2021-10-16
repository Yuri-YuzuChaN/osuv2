from .api import PPApi

class PPCalc:

    def __init__(self, mode: int, mapid: int) -> None:
        self.mapid: int = mapid
        self.mode: int = mode

    def __data(self, mode: int, info: dict):
        self.acc = int(info['Accuracy'])
        self.combo = info['Combo']
        self.c300 = info['Great']
        self.miss = info['Miss']
        self.pp = int(info['pp'])
        self.ifpp = int(info['ifpp'])
        self.stars = info['mapinfo']['star_rating']
        if mode == 0:
            self.aim = int(info['Aim'])
            self.max_combo = info['Max Combo']
            self.c50 = info['Meh']
            self.od = info['OD']
            self.c100 = info['Ok']
            self.speed = int(info['Speed'])
            self.ar = info['mapinfo']['ar_rating']
            self.od = info['mapinfo']['od_rating']
            self.sspp = int(info['accpp'][-1])
        elif mode == 1:
            self.c100 = info['Ok']
            self.strain = info['Strain']
            self.c50 = info['Meh']
        elif mode == 2:
            pass
        else:
            self.c100 = info['Ok']
            self.strain = info['Strain']
            self.perfect = info['Perfect']

    async def if_pp(self, mods: list) -> int:
        info = await PPApi(self.mode, self.mapid, mods=mods)
        self.__data(self.mode, info)
        if self.mode == 0:
            return self.ifpp, self.stars, self.ar, self.od
        else:
            return self.ifpp, self.stars

    async def osu_pp(self, acc: float, combo: int, c100: int, c50: int, miss: int, mods: list):
        info = await PPApi(0, self.mapid, acc * 100, combo, c100, c50, miss=miss, mods=mods)
        self.__data(self.mode, info)
        return self.pp, self.ifpp, self.sspp, self.aim, self.speed, self.acc, self.stars, self.ar, self.od

    async def taiko_pp(self, acc: float, combo: int, c100: int, miss: int, mods: list):
        info = await PPApi(1, self.mapid, acc * 100, combo, c100, miss=miss, mods=mods)
        self.__data(self.mode, info)
        return self.pp, self.ifpp, self.stars

    async def catch_pp(self, acc: float, combo: int, miss: int, mods: list):
        info = await PPApi(2, self.mapid, acc * 100, combo, miss=miss, mods=mods)
        self.__data(self.mode, info)
        return self.pp, self.ifpp, self.stars

    async def mania_pp(self, score: int, mods: list):
        info = await PPApi(3, self.mapid, score=score, mods=mods)
        self.__data(self.mode, info)
        return self.pp, self.ifpp, self.stars
