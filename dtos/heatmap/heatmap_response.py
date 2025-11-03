from pydantic import BaseModel
from typing import List
from .heatmap_cicrle import HeatmapCircle
from models import Relato


class pointsResponse(BaseModel):
    lat: float
    long: float


class HeatmapResponse(BaseModel):
    circles: List[HeatmapCircle]
    points: List[pointsResponse]

