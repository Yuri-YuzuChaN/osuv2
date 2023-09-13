from typing import List, Optional

from pydantic import BaseModel, Field


class Level(BaseModel):

    current: int = 0
    progress: int = 0


class GradeCounts(BaseModel):

    ss: int
    ssh: int
    s: int
    sh: int
    a: int


class Variants(BaseModel):

    mode: str
    variant: str
    country_rank: int
    global_rank: int
    pp: float


class Statistics(BaseModel):

    level: Level
    pp: Optional[float] = 0
    global_rank: Optional[int] = 0
    ranked_score: Optional[int] = 0
    accuracy: Optional[float] = Field(alias='hit_accuracy')
    play_count: Optional[int] = 0
    play_time: Optional[int] = 0
    total_score: Optional[int] = 0
    total_hits: Optional[int] = 0
    maximum_combo: Optional[int] = 0
    is_ranked: bool
    grade_counts: GradeCounts
    country_rank: int
    variants: Optional[List[Variants]]


class UserAchievements(BaseModel):

    achieved_at: str
    achievement_id: int


class History(BaseModel):

    mode: str
    data: List[int]


class User(BaseModel):
    
    avatar_url: str
    country_code: str
    id: int
    is_online: bool
    is_supporter: bool
    last_visit: str
    username: str
    cover_url: Optional[str] = ''
    join_date: Optional[str] = ''
    play_mode: Optional[int] = 0
    statistics: Optional[Statistics]
    user_achievements: Optional[List[UserAchievements]]
    rankHistory: Optional[History]
