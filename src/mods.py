from typing import List, Optional

from .. import NewMod
from .Model import Score


class Mods:
    
    tempMods: Optional[int]

    def __init__(self, scoreList: List[Score], mods: List[str]) -> None:
        self.ScoreList = scoreList
        self.Sum = self.calcModsValue(mods)


    def calcModsValue(self, mods: List[str]) -> int:
        temp = 0
        for mod in mods:
            temp += int(NewMod[mod])
        return temp


    def findModsIndex(self) -> Optional[List[int]]:
        """获取当前 `mods` 的列表"""
        listIndex = []
        for index, value in enumerate(self.ScoreList):
            if self.calcModsValue(value.mods) == self.Sum:
                listIndex.append(index)
        return listIndex