from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.sos_request import SOSRequest
from app.repositories.sos_request import SOSRequestRepository
from app.repositories.user import UserRepository
from app.repositories.emergency_contact import EmergencyContactRepository
from app.repositories.live_location import LiveLocationRepository
from app.services.fcm import FCMNotificationService
from app.schemas.sos_request import SOSRequestCreate


class SOSService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.sos_repo = SOSRequestRepository(db)
        self.user_repo = UserRepository(db)
        self.contact_repo = EmergencyContactRepository(db)
        self.location_repo = LiveLocationRepository(db)

    async def create_sos(self, user_id: str, sos_in: SOSRequestCreate) -> SOSRequest:
        user = await self.user_repo.get(user_id)
        if not user:
            raise ValueError("User not found")

        # Create SOS request record
        sos_dict = {
            "user_id": user_id,
            "accident_id": sos_in.accident_id,
            "status": "active",
        }
        sos = await self.sos_repo.create(sos_dict)

        # Notify emergency contacts with SOS Alert
        try:
            contacts = await self.contact_repo.get_by_user(user_id)
            tokens = []
            for c in contacts:
                contact_user = await self.user_repo.get_by_phone(c.phone)
                if contact_user and contact_user.fcm_token:
                    tokens.append(contact_user.fcm_token)

            if tokens:
                # Find current coordinates for alert payload
                current_loc = await self.location_repo.get_by_user(user_id)
                lat, lon = (0.0, 0.0)
                if current_loc:
                    lat, lon = current_loc.latitude, current_loc.longitude
                maps_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"

                FCMNotificationService.send_sos_alert(
                    contact_tokens=tokens,
                    victim_name=user.name,
                    maps_link=maps_link,
                )
        except Exception:
            pass

        return sos

    async def get_active_sos(self) -> List[SOSRequest]:
        return await self.sos_repo.get_active_requests()
