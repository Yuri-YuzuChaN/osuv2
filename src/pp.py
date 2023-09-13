from .Api import osuApi
from .Error import PPError
from .Model import PP, Score


class PPCalc:

    def __init__(self, score: Score) -> None:
        self.score = score
        self.beatmap = score.beatmap


    async def calc(self, *, isPlay: bool = True) -> PP:
        data = {
            'BeatmapID': self.beatmap.id,
            'Mode': self.score.mode_int,
            'Accuracy': self.score.accuracy,
            'C300': self.score.statistics.count_300,
            'C100': self.score.statistics.count_100,
            'C50': self.score.statistics.count_50,
            'Miss': self.score.statistics.count_miss,
            'Mods': ''.join(self.score.mods),
            'isPlay': str(isPlay)
        }
        if self.score.mode_int != 3:
            data['Combo'] = self.score.max_combo
        if self.score.mode_int == 2 or self.score.mode_int == 3:
            data['Katu'] = self.score.statistics.count_katu
        if self.score.mode_int == 3:
            data['Score'] = self.score.score
            data['Geki'] = self.score.statistics.count_geki
        try:
            pp = await osuApi.pp(data)
            return PP(**pp)
        except Exception as e:
            raise PPError