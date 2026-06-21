import math
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.volunteer import Volunteer
from app.schemas.volunteer import VolunteerResponse, VolunteerNearbyResponse, VolunteerCreate, VolunteerUpdate


class VolunteerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
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

    async def register_volunteer(self, vol_in: VolunteerCreate) -> Volunteer:
        existing = await self.db.execute(select(Volunteer).where(Volunteer.phone == vol_in.phone))
        vol = existing.scalar_one_or_none()
        if vol:
            raise ValueError("Volunteer already registered with this phone number")

        vol = Volunteer(
            name=vol_in.name,
            phone=vol_in.phone,
            latitude=vol_in.latitude,
            longitude=vol_in.longitude,
            training_level=vol_in.training_level,
            is_available=vol_in.is_available,
        )
        self.db.add(vol)
        await self.db.flush()
        return vol

    async def update_status(self, phone: str, vol_up: VolunteerUpdate) -> Volunteer | None:
        query = select(Volunteer).where(Volunteer.phone == phone)
        result = await self.db.execute(query)
        vol = result.scalar_one_or_none()
        if not vol:
            return None

        update_data = vol_up.model_dump(exclude_unset=True)
        for field, val in update_data.items():
            setattr(vol, field, val)

        self.db.add(vol)
        await self.db.flush()
        return vol

    async def get_nearby_volunteers(
        self, lat: float, lon: float, max_radius_km: float = 5.0, limit: int = 5
    ) -> List[VolunteerNearbyResponse]:
        query = select(Volunteer).where(Volunteer.is_available == True)
        result = await self.db.execute(query)
        all_vols = result.scalars().all()

        nearby = []
        for v in all_vols:
            dist = self.haversine_distance(lat, lon, v.latitude, v.longitude)
            if dist <= max_radius_km:
                nearby.append(
                    VolunteerNearbyResponse(
                        volunteer=VolunteerResponse.model_validate(v),
                        distance_km=round(dist, 2),
                    )
                )

        nearby.sort(key=lambda x: x.distance_km)
        return nearby[:limit]
