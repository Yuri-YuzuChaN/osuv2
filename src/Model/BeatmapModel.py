from typing import Optional

from pydantic import BaseModel, Field


class Covers(BaseModel):
    
    cover: str
    cover2x: str = Field(alias='cover@2x')
    card: str
    card2x: str = Field(alias='card@2x')
    list: str
    list2x: str = Field(alias='list@2x')
    slimcover: str
    slimcover2x: str = Field(alias='slimcover@2x')


class BeatmapSet(BaseModel):
    
    artist: str
    artist_unicode: Optional[str]
    covers: Covers
    creator: str
    favourite_count: int
    id: int
    play_count: int
    preview_url: str
    source: str
    title: str
    title_unicode: Optional[str]
    user_id: int
    ranked: Optional[int]
    ranked_date: Optional[str] = None
    status: str


class Beatmap(BaseModel):
    
    beatmapset_id: int
    difficulty_rating: float
    id: int
    total_length: int
    version: str
    accuracy: float
    ar: float
    bpm: int
    count_circles: int
    count_sliders: int
    count_spinners: int
    cs: int
    drain: int
    hit_length: int
    mode_int: int
    ranked: int
    url: str
    beatmapset: Optional[BeatmapSet]
    max_combo: Optional[int] = 0
