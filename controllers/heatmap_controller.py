from datetime import datetime
from typing import Optional
from dtos.heatmap.heatmap_cicrle import HeatmapCircle
from fastapi import APIRouter, Query
from haversine import haversine, Unit
from dtos.heatmap.heatmap_response import HeatmapResponse, pointsResponse

from database import SessionDep
from sqlmodel import select
import numpy as np
from sklearn.cluster import DBSCAN


from models import Relato

router = APIRouter(prefix="/heatmap", tags=["Mapa de Calor"])


@router.get("")
def get_heatmap_data(
        session: SessionDep,
        start_date: Optional[datetime] = Query(None, description="Data inicial (ISO format) para filtrar os relatos"),
        end_date: Optional[datetime] = Query(None, description="Data final (ISO format) para filtrar os relatos"),
        eps_km: float = Query(0.5, description="Raio de busca (em Km) para agrupar pontos em um cluster.", gt=0),
        min_samples: int = Query(3, description="Número mínimo de relatos para formar um cluster.", gt=0)
):
    """
        **Descrição:** Processa todos os relatos (podendo filtrar por data) e os agrupa
        em 'clusters' (círculos) para exibição no mapa de calor.
        Utiliza o algoritmo DBSCAN para encontrar áreas com alta concentração de relatos.

        **Parâmetros de Query:**
        - `start_date` (Opcional): Filtra relatos a partir desta data/hora.
        - `end_date` (Opcional): Filtra relatos até esta data/hora.
        - `eps_km`: O raio (em km) que o algoritmo usa para agrupar pontos.
        - `min_samples`: O número mínimo de relatos necessários dentro do raio `eps_km`
          para formar um cluster.

        """
    query = select(Relato)
    if start_date:
        query = query.where(Relato.data_furto >= start_date)
    if end_date:
        query = query.where(Relato.data_furto <= end_date)

    relatos = session.exec(query).all()

    points: list[pointsResponse]= []

    for relato in relatos:
        points.append(pointsResponse(lat=relato.latitude, long=relato.longitude))



    if len(relatos) < min_samples:
        # Não há dados suficientes para clusterizar
        return HeatmapResponse(circles=[], points=points)

    # 2. Prepara os dados para o DBSCAN
    # Coordenadas em [latitude, longitude]
    coords = np.array([[r.latitude, r.longitude] for r in relatos])

    # DBSCAN usa a métrica 'haversine' que espera coordenadas em radianos
    coords_radians = np.radians(coords)

    # 3. Executa o DBSCAN
    # Converte o 'eps' (raio de busca) de Km para radianos
    earth_radius_km = 6371.0
    eps_rad = eps_km / earth_radius_km

    # Roda o algoritmo
    db = DBSCAN(eps=eps_rad, min_samples=min_samples, metric='haversine').fit(coords_radians)

    cluster_labels = db.labels_
    unique_labels = set(cluster_labels)

    heatmap_circles = []

    # 4. Processa cada cluster encontrado
    for label in unique_labels:
        if label == -1:
            # label -1 é "ruído" (pontos que não pertencem a nenhum cluster)
            continue

        # Pega os pontos (em graus) que pertencem a este cluster
        cluster_mask = (cluster_labels == label)
        cluster_points_coords = coords[cluster_mask]

        # 4a. Calcula o "peso" (quantos pontos tem no cluster)
        weight = len(cluster_points_coords)

        # 4b. Calcula o centro do cluster (média das latitudes e longitudes)
        center = cluster_points_coords.mean(axis=0)
        center_lat, center_lon = center[0], center[1]

        # 4c. Calcula o raio (distância máxima do centro a qualquer ponto do cluster)
        max_radius_meters = 0
        center_tuple = (center_lat, center_lon)

        for point in cluster_points_coords:
            point_tuple = (point[0], point[1])
            distance = haversine(center_tuple, point_tuple, unit=Unit.METERS)
            if distance > max_radius_meters:
                max_radius_meters = distance

        heatmap_circles.append(
            HeatmapCircle(
                latitude=center_lat,
                longitude=center_lon,
                radius_meters=max_radius_meters,
                weight=weight
            )
        )

    return HeatmapResponse(circles=heatmap_circles, points=points)