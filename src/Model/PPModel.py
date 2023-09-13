from typing import Optional

from pydantic import BaseModel


class PP(BaseModel):
    
    StarRating: float
    HP: float
    CS: float
    Aim: float
    Speed: float
    AR: Optional[float]
    OD: Optional[float]
    aim: Optional[float]
    speed: Optional[float]
    accuracy: Optional[float]
    pp: float
    ifpp: float
    sspp: float