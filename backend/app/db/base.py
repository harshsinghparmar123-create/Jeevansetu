# Import all models so Alembic can discover them
from app.models.base import Base # noqa
from app.models.user import User # noqa
from app.models.emergency_contact import EmergencyContact # noqa
from app.models.accident import Accident # noqa
from app.models.live_location import LiveLocation # noqa
from app.models.hospital import Hospital # noqa
from app.models.sos_request import SOSRequest # noqa
from app.models.volunteer import Volunteer # noqa
from app.models.ambulance import Ambulance # noqa
from app.models.authority_alert import AuthorityAlert # noqa
