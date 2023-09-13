from typing import List, Optional

from pydantic import BaseModel


class BidData(BaseModel):
    
    AR: float
    CS: float
    HP: float
    OD: float
    aim: float
    bid: int
    circles: int
    length: int
    maxcombo: int
    mode: int
    pp: int
    pp_acc: float
    pp_aim: float
    pp_speed: float
    sliders: int
    speed: float
    star: float
    version: str


class Sayomap(BaseModel):
    
    approved_date: int
    artist: str
    artistU: Optional[str]
    bid_data: List[BidData]
    bids_amount: int
    bpm: float
    creator: str
    creator_id: int
    sid: int
    source: Optional[str]
    title: str
    titleU: Optional[str]
    