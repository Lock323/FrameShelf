import pytest
import jwt
import time
from unittest.mock import patch, MagicMock
from src.auth.jwt_handler import AccessTokenManager
from jwt import InvalidSignatureError

class TestAccessTokenManager:
    @pytest.fixture
    def token_manager(self):
        return AccessTokenManager()

    @pytest.fixture
    def user_data(self):
        return {
            "email": "test@example.com",
            "username": "testuser",
            "id": 1
        }

    @pytest.fixture
    def mock_settings(self):
        return MagicMock(
            JWT_SECRET="test_secret",
            JWT_ALGORITHM="HS256"
        )

    def test_sign_token_success(self, token_manager, user_data, mock_settings):
        with patch('src.auth.jwt_handler.settings', mock_settings):
            result = token_manager.sign_token(
                user_data["email"],
                user_data["username"],
                user_data["id"]
            )
            assert "access_token" in result
            decoded = jwt.decode(
                result["access_token"],
                mock_settings.JWT_SECRET,
                algorithms=[mock_settings.JWT_ALGORITHM]
            )
            assert decoded["email"] == user_data["email"]
            assert decoded["username"] == user_data["username"]
            assert decoded["id"] == user_data["id"]
            assert decoded["purpose"] == "login_user"
            assert decoded["expires"] > time.time()

    def test_decode_token_valid(self, token_manager, user_data, mock_settings):
        with patch('src.auth.jwt_handler.settings', mock_settings):
            payload = {
                **user_data,
                "expires": time.time() + 3600,
                "purpose": "login_user"
            }
            token = jwt.encode(payload, mock_settings.JWT_SECRET, algorithm=mock_settings.JWT_ALGORITHM)
            result = token_manager.decode_token(token)
            assert result is not None
            assert result["email"] == user_data["email"]
            assert result["username"] == user_data["username"]
            assert result["id"] == user_data["id"]

    def test_decode_token_expired(self, token_manager, user_data, mock_settings):
        with patch('src.auth.jwt_handler.settings', mock_settings):
            payload = {
                **user_data,
                "expires": time.time() - 3600,
                "purpose": "login_user"
            }
            token = jwt.encode(payload, mock_settings.JWT_SECRET, algorithm=mock_settings.JWT_ALGORITHM)
            result = token_manager.decode_token(token)
            assert result is None


    def test_decode_token_invalid_signature(self, token_manager, user_data, mock_settings):
        with patch('src.auth.jwt_handler.settings', mock_settings):
            payload = {
                **user_data,
                "expires": time.time() + 3600,
                "purpose": "login_user"
            }
            invalid_token = jwt.encode(payload, "wrong_secret", algorithm=mock_settings.JWT_ALGORITHM)

            with pytest.raises(InvalidSignatureError):
                token_manager.decode_token(invalid_token)

    def test_decode_token_wrong_purpose(self, token_manager, user_data, mock_settings):
        with patch('src.auth.jwt_handler.settings', mock_settings):
            payload = {
                **user_data,
                "expires": time.time() + 3600,
                "purpose": "wrong_purpose"
            }
            token = jwt.encode(payload, mock_settings.JWT_SECRET, algorithm=mock_settings.JWT_ALGORITHM)
            result = token_manager.decode_token(token)
            assert result is None
