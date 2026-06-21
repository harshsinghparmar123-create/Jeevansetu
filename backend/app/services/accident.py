import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.model_service import AISeverityService
from app.models.accident import Accident
from app.repositories.accident import AccidentRepository
from app.repositories.user import UserRepository
from app.repositories.emergency_contact import EmergencyContactRepository
from app.services.fcm import FCMNotificationService
from app.schemas.accident import AccidentCreate


class AccidentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.accident_repo = AccidentRepository(db)
        self.user_repo = UserRepository(db)
        self.contact_repo = EmergencyContactRepository(db)

    async def report_accident(self, user_id: str, accident_in: AccidentCreate) -> Accident:
        # Fetch user
        user = await self.user_repo.get(user_id)
        if not user:
            raise ValueError("User not found")

        # Run AI prediction (severity and score)
        # response_delay is defaulted to 0 for initial report
        ai_res = AISeverityService.predict_severity(
            impact_force=accident_in.impact_force,
            speed=accident_in.speed,
            orientation_change=accident_in.orientation_change,
            response_delay=0.0,
        )

        # Create database object
        accident_dict = {
            "user_id": user_id,
            "latitude": accident_in.latitude,
            "longitude": accident_in.longitude,
            "impact_force": accident_in.impact_force,
            "speed": accident_in.speed,
            "orientation_change": accident_in.orientation_change,
            "severity": ai_res["severity"],
            "risk_score": ai_res["score"],
            "status": "pending",
        }
        accident = await self.accident_repo.create(accident_dict)

        # Notify emergency contacts via FCM
        try:
            contacts = await self.contact_repo.get_by_user(user_id)
            tokens = []
            for c in contacts:
                # Find matching user registered in system by phone number
                contact_user = await self.user_repo.get_by_phone(c.phone)
                if contact_user and contact_user.fcm_token:
                    tokens.append(contact_user.fcm_token)

            if tokens:
                maps_link = f"https://www.google.com/maps/search/?api=1&query={accident.latitude},{accident.longitude}"
                FCMNotificationService.notify_emergency_contacts(
                    contact_tokens=tokens,
                    victim_name=user.name,
                    accident_id=str(accident.id),
                    maps_link=maps_link,
                )
        except Exception:
            # Silence exceptions in notifications to ensure report transaction completes successfully
            pass

        return accident

    async def get_accident(self, accident_id: str) -> Accident | None:
        return await self.accident_repo.get(accident_id)
