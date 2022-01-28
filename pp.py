from .api import PPApi

class PPCalc:

    def __init__(self, mode: int, mapid: int) -> None:
        self.mapid: int = mapid
        self.mode: int = mode

    def __data__(self, mode: int, info: dict):
        score = info['score']
        statistics = score['statistics']
        performance = info['performance_attributes']
        difficulty = info['difficulty_attributes']
        self.combo = score['combo']
        self.c300 = statistics['Great']
        self.miss = statistics['Miss']
        self.pp = int(performance['pp'])
        self.ifpp = int(performance['ifpp'])
        self.stars = float(f'{difficulty["star_rating"]:.2f}')
        if mode == 0:
            self.aim = int(performance['aim'])
            self.acc = int(performance['accuracy'])
            self.max_combo = difficulty['max_combo']
            self.c50 = statistics['Meh']
            self.c100 = statistics['Ok']
            self.speed = int(performance['speed'])
            self.ar = float(f'{difficulty["approach_rate"]:.1f}')
            self.od = float(f'{difficulty["overall_difficulty"]:.1f}')
            self.sspp = int(performance['accpp'][-1])
        elif mode == 1:
            self.c100 = statistics['Ok']
            self.c50 = statistics['Meh']
        elif mode == 2:
            pass
        else:
            self.c100 = statistics['Ok']
            self.perfect = statistics['Perfect']

    async def if_pp(self, mods: list) -> int:
        info = await PPApi(self.mode, self.mapid, mods=mods)
        self.__data__(self.mode, info)
        if self.mode == 0:
            return self.ifpp, self.stars, self.ar, self.od
        else:
            return self.ifpp, self.stars

    async def osu_pp(self, acc: float, combo: int, c300: int, c100: int, c50: int, miss: int, mods: list):
        info = await PPApi(0, self.mapid, acc * 100, combo, c300, c100, c50, miss=miss, mods=mods)
        self.__data__(self.mode, info)
        return self.pp, self.ifpp, self.sspp, self.aim, self.speed, self.acc, self.stars, self.ar, self.od

    async def taiko_pp(self, acc: float, combo: int, c100: int, miss: int, mods: list):
        info = await PPApi(1, self.mapid, acc * 100, combo, good=c100, miss=miss, mods=mods)
        self.__data__(self.mode, info)
        return self.pp, self.ifpp, self.stars

    async def catch_pp(self, acc: float, combo: int, miss: int, mods: list):
        info = await PPApi(2, self.mapid, acc * 100, combo, miss=miss, mods=mods)
        self.__data__(self.mode, info)
        return self.pp, self.ifpp, self.stars

    async def mania_pp(self, score: int, mods: list):
        info = await PPApi(3, self.mapid, score=score, mods=mods)
        self.__data__(self.mode, info)
        return self.pp, self.ifpp, self.stars
