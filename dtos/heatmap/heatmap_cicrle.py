from pydantic import BaseModel


class HeatmapCircle(BaseModel):
    latitude: float
    longitude: float
    radius_meters: float
    weight: int