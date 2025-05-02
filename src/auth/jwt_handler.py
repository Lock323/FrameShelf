import jwt
import time
from config import settings
import hashlib

class AccessTokenManager:

    def sign_token(self, user_email: str, username: str, user_id: int) -> dict:
        payload = {
            "email": user_email,
            "username": username,
            "id": user_id,
            "expires": time.time() + 3600,
            "purpose": "login_user"
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        return {"access_token": token}

    def decode_token(self, token: str) -> str | None:
        decoded_token = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        if decoded_token["purpose"] != "login_user":
            return None
        return decoded_token if decoded_token["expires"] >= time.time() else None



class ResetPWTokenManager:

    def sign_token(self, user_id: int, user_hashed_pw: str) -> dict:
        payload = {
            "id": user_id,
            "key": hashlib.sha256(user_hashed_pw.encode()).hexdigest()[0:6],
            "expires": time.time() + 600,
            "purpose": "reset_password"
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        return {"reset_pw_token": token}

    def decode_token(self, token: str, user_hashed_pw: str) -> str | None:
        decoded_token = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        if decoded_token["purpose"] != "reset_password":
            return None
        current_key = hashlib.sha256(user_hashed_pw.encode()).hexdigest()[0:6]
        if current_key != decoded_token["key"]:
            return None
        return decoded_token if decoded_token["expires"] >= time.time() else None



access_token_manager = AccessTokenManager()
reset_pw_token_manager = ResetPWTokenManager()


