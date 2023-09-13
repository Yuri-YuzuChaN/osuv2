from typing import List, Optional, Union

from pydantic import BaseModel

from .BeatmapModel import Beatmap, BeatmapSet
from .UserModel import User


class Statistics(BaseModel):
    
    count_100: int
    count_300: int
    count_50: int
    count_geki: int
    count_katu: int
    count_miss: int


class Weight(BaseModel):
    
    percentage: float
    pp: float


class Score(BaseModel):
    
    accuracy: float
    best_id: Optional[int]
    created_at: Optional[str]
    max_combo: Optional[int]
    mode: Optional[str]
    mode_int: int
    mods: List[Optional[str]]
    pp: float = -1
    rank: Optional[str]
    score: Optional[int]
    statistics: Statistics
    beatmap: Beatmap
    beatmapset: Optional[BeatmapSet]
    user: Optional[User]
    weight: Optional[Weight]
    

class BestScore(BaseModel):
    
    position: Union[int, str]
    score: Score