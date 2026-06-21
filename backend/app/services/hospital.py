import math
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.hospital import HospitalRepository
from app.schemas.hospital import HospitalRecommendationResponse, HospitalResponse


class HospitalRecommendationService:
    def __init__(self, db: AsyncSession):
        self.hospital_repo = HospitalRepository(db)

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        # Distance in kilometers
        r = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c

    async def get_nearby_hospitals(
        self, lat: float, lon: float, limit: int = 5
    ) -> List[HospitalRecommendationResponse]:
        hospitals = await self.hospital_repo.get_multi()
        recommendations = []

        for h in hospitals:
            dist = self.haversine_distance(lat, lon, h.latitude, h.longitude)
            # Estimate travel time based on simple avg speed of 45 km/h in urban emergency environments
            eta = (dist / 45.0) * 60.0  # minutes

            # Calculate bonuses (higher resources decreases the penalty score)
            trauma_bonus = 0.0
            if h.trauma_level == 1:
                trauma_bonus = 15.0
            elif h.trauma_level == 2:
                trauma_bonus = 8.0
            elif h.trauma_level == 3:
                trauma_bonus = 3.0

            resource_bonus = (h.available_beds * 0.5) + (h.ventilators * 1.5)
            # Cap resource bonus at 20.0 to prevent outlier distortion
            resource_bonus = min(resource_bonus, 20.0)

            # Score formula: Lower score is better. Distance & ETA add to the score, capabilities/availability subtract.
            score = (dist * 1.5) + (eta * 1.0) - trauma_bonus - resource_bonus

            # Prepare schema representation
            h_resp = HospitalResponse.model_validate(h)
            recommendations.append(
                HospitalRecommendationResponse(
                    hospital=h_resp,
                    score=round(score, 2),
                    estimated_travel_time_mins=round(eta, 1),
                    distance_km=round(dist, 2),
                )
            )

        # Sort recommendations by score ascending (lowest score first)
        recommendations.sort(key=lambda x: x.score)
        return recommendations[:limit]

    async def get_best_hospital(
        self, lat: float, lon: float
    ) -> HospitalRecommendationResponse | None:
        recs = await self.get_nearby_hospitals(lat, lon, limit=1)
        return recs[0] if recs else None
