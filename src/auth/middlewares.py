from fastapi import Request
from auth.jwt_handler import access_token_manager
from auth.schemas import UserInfo
from exceptions import InvalidLoginTokenError


class AuthGuard:
    def __init__(self, raise_exc=False):
        self.raise_exc = raise_exc

    async def __call__(self, request: Request):
        try:
            token = request.cookies["access_token"]
            decoded_token = access_token_manager.decode_token(token)
            if decoded_token is None and self.raise_exc is False:
                return None
            elif decoded_token is None and self.raise_exc is True:
                raise InvalidLoginTokenError()
            return UserInfo(username=decoded_token["username"], email=decoded_token["email"], id=decoded_token["id"])
        except KeyError:
            if self.raise_exc is False:
                return None
            raise InvalidLoginTokenError()


auth_guard_exc_true = AuthGuard(raise_exc=True)
auth_guard_exc_false = AuthGuard(raise_exc=False)

