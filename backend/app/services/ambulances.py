import math
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ambulance import Ambulance
from app.models.accident import Accident
from app.schemas.ambulance import AmbulanceCreate, AmbulanceUpdate, AmbulanceResponse, AmbulanceETAResponse


class AmbulanceService:
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

    async def register_ambulance(self, amb_in: AmbulanceCreate) -> Ambulance:
        existing = await self.db.execute(
            select(Ambulance).where(Ambulance.license_plate == amb_in.license_plate)
        )
        amb = existing.scalar_one_or_none()
        if amb:
            raise ValueError("Ambulance already registered with this license plate")

        amb = Ambulance(
            name=amb_in.name,
            license_plate=amb_in.license_plate,
            latitude=amb_in.latitude,
            longitude=amb_in.longitude,
            status=amb_in.status,
        )
        self.db.add(amb)
        await self.db.flush()
        return amb

    async def update_status(self, license_plate: str, amb_up: AmbulanceUpdate) -> Ambulance | None:
        query = select(Ambulance).where(Ambulance.license_plate == license_plate)
        result = await self.db.execute(query)
        amb = result.scalar_one_or_none()
        if not amb:
            return None

        update_data = amb_up.model_dump(exclude_unset=True)
        for field, val in update_data.items():
            setattr(amb, field, val)

        self.db.add(amb)
        await self.db.flush()
        return amb

    async def dispatch_ambulance(self, ambulance_id: str, accident_id: str) -> Ambulance:
        import uuid
        amb_uid = uuid.UUID(ambulance_id) if isinstance(ambulance_id, str) else ambulance_id
        query = select(Ambulance).where(Ambulance.id == amb_uid)
        result = await self.db.execute(query)
        amb = result.scalar_one_or_none()
        if not amb:
            raise ValueError("Ambulance not found")

        amb.status = "dispatched"
        self.db.add(amb)
        await self.db.flush()
        return amb

    async def get_eta(self, accident_id: str) -> Optional[AmbulanceETAResponse]:
        # Fetch accident
        import uuid
        acc_uid = uuid.UUID(accident_id) if isinstance(accident_id, str) else accident_id
        accident_query = select(Accident).where(Accident.id == acc_uid)
        accident_result = await self.db.execute(accident_query)
        accident = accident_result.scalar_one_or_none()
        if not accident:
            return None

        # Fetch nearest available or dispatched ambulance
        query = select(Ambulance).where(Ambulance.status != "busy").limit(10)
        result = await self.db.execute(query)
        all_ambs = result.scalars().all()

        if not all_ambs:
            return None

        # Find closest
        best_amb = None
        min_dist = float("inf")
        for amb in all_ambs:
            dist = self.haversine_distance(
                accident.latitude, accident.longitude, amb.latitude, amb.longitude
            )
            if dist < min_dist:
                min_dist = dist
                best_amb = amb

        if not best_amb:
            return None

        # ETA based on avg speed of 50 km/h
        eta_mins = (min_dist / 50.0) * 60.0
        return AmbulanceETAResponse(
            ambulance=AmbulanceResponse.model_validate(best_amb),
            estimated_travel_time_mins=round(eta_mins, 1),
            distance_km=round(min_dist, 2),
        )
