# controllers/location_controller.py
import os
import requests
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/location", tags=["Location"])
GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


@router.get("/reverse")
def reverse_geocode(lat: float, lng: float):
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=503, detail="Serviço de geocoding não configurado.")

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"latlng": f"{lat},{lng}", "key": GOOGLE_API_KEY, "language": "pt-BR"}

    try:
        resp = requests.get(url, params=params)
        data = resp.json()

        if data.get("status") == "OK" and data.get("results"):
            # Retorna o endereço formatado ou estrutura personalizada
            return {"address": data["results"][0]["formatted_address"]}

        return {"address": "Endereço não encontrado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))