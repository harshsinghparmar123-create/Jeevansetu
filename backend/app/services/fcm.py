import os
import firebase_admin
from firebase_admin import credentials, messaging
from app.core.config import settings
from app.core.logging import logger

# Initialize Firebase App if credential file exists
firebase_initialized = False
try:
    if os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
        firebase_initialized = True
        logger.info("Firebase Admin SDK successfully initialized.")
    else:
        logger.warning(
            f"Firebase key not found at {settings.FIREBASE_CREDENTIALS_PATH}. Running FCM in MOCK logging mode."
        )
except Exception as e:
    logger.error(f"FCM Initialization failed: {e}. Falling back to MOCK mode.")


class FCMNotificationService:
    @staticmethod
    def send_multicast_notification(
        tokens: list[str], title: str, body: str, data: dict = None
    ) -> bool:
        if not tokens:
            return False

        logger.info(
            f"FCM Broadcast — Title: '{title}' | Body: '{body}' | Recipients: {len(tokens)}"
        )

        valid_tokens = [t for t in tokens if t]
        if not valid_tokens:
            return False

        if firebase_initialized:
            try:
                message = messaging.MulticastMessage(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    data=data or {},
                    tokens=valid_tokens,
                )
                response = messaging.send_multicast(message)
                logger.info(
                    f"FCM dispatch success. Sent: {response.success_count}, Failed: {response.failure_count}"
                )
                return response.failure_count == 0
            except Exception as e:
                logger.error(f"Firebase Multicast delivery error: {e}")
                return False
        else:
            # Mock Logging Output
            logger.info("--- MOCK FCM NOTIFICATION SENT ---")
            logger.info(f"TO TOKENS: {valid_tokens}")
            logger.info(f"TITLE: {title}")
            logger.info(f"BODY: {body}")
            logger.info(f"DATA PAYLOAD: {data}")
            logger.info("----------------------------------")
            return True

    @classmethod
    def notify_emergency_contacts(
        cls, contact_tokens: list[str], victim_name: str, accident_id: str, maps_link: str
    ):
        title = "⚠ EMERGENCY: Possible Accident Detected!"
        body = f"{victim_name} may have been in a crash. Click to track location."
        payload = {
            "type": "accident_alert",
            "accident_id": str(accident_id),
            "maps_link": maps_link,
            "victim_name": victim_name,
        }
        return cls.send_multicast_notification(contact_tokens, title, body, payload)

    @classmethod
    def send_sos_alert(
        cls, contact_tokens: list[str], victim_name: str, maps_link: str
    ):
        title = "🚨 EMERGENCY SOS ACTIVATED!"
        body = f"{victim_name} has manually activated SOS. Click to track their live coordinates."
        payload = {
            "type": "sos_alert",
            "maps_link": maps_link,
            "victim_name": victim_name,
        }
        return cls.send_multicast_notification(contact_tokens, title, body, payload)
