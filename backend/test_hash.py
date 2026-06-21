import traceback
from app.core import security

try:
    print("Testing password hashing...")
    h = security.get_password_hash("securepassword123")
    print("HASHED SUCCESS:", h)
except Exception as e:
    traceback.print_exc()
