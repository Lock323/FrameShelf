from passlib.context import CryptContext
from auth.models import Users
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import PlainTextResponse
from sqlalchemy import select, update
from auth.jwt_handler import AccessTokenManager
from auth.schemas import UserCreate, UserLogin
from datetime import datetime, timezone


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserManager:

    async def get_by_email(self, user_email, session: AsyncSession) -> Users | None:
        existing_user = await session.execute(select(Users).where(Users.email == user_email))
        existing_user_data = existing_user.scalar_one_or_none()
        return existing_user_data

    async def add_to_db(self, user_data: UserCreate, session: AsyncSession):
        hashed_password = pwd_context.hash(user_data.password)
        new_user = Users(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            created_at=datetime.now(tz=timezone.utc)
        )
        session.add(new_user)
        await session.commit()
        return new_user.id

    async def reset_password(self, session: AsyncSession, new_password: str, user_email: str):
        hashed_password = pwd_context.hash(new_password)
        await session.execute(update(Users).where(Users.email == user_email).values(hashed_password=hashed_password))
        await session.commit()

    async def check_credentials(self, user_data: UserLogin, session: AsyncSession):
        hashed_password = await session.execute(select(Users.hashed_password).where(Users.email == user_data.email))
        hashed_password = hashed_password.scalar_one_or_none()
        if hashed_password:
            existing_pwd = pwd_context.verify(user_data.password, hashed_password)
            if existing_pwd:
                return True
        return False

    async def create_user(self, user_data: UserCreate, session: AsyncSession,
                          token_manager: AccessTokenManager):
        existing_user = await self.get_by_email(user_email=user_data.email, session=session)
        if existing_user:
            return PlainTextResponse('User with this email already exists', status_code=422)
        user_id = await self.add_to_db(user_data=user_data, session=session)
        token = token_manager.sign_token(user_email=user_data.email, username=user_data.username, user_id=user_id)
        response = PlainTextResponse(status_code=302)
        response.headers["HX-Redirect"] = "/home"
        response.set_cookie(
            key="access_token",
            value=token["access_token"],
            httponly=True,
            max_age=6000
        )
        return response

    async def login_user(self, user_data: UserLogin, session: AsyncSession,
                         token_manager: AccessTokenManager, referer: str):
        credentials = await self.check_credentials(user_data=user_data, session=session)
        if credentials:
            user = await self.get_by_email(session=session, user_email=user_data.email)
            token = token_manager.sign_token(user_email=user.email, username=user.username, user_id=user.id)
            response = PlainTextResponse(status_code=301)
            referer = '/' if referer == "None" or "/reset_pw" else referer
            response.headers["HX-Redirect"] = referer
            response.set_cookie(
                key="access_token",
                value=token["access_token"],
                httponly=True,
                max_age=6000
            )
            return response
        return PlainTextResponse('Wrong e-mail or password', status_code=422)

user_manager = UserManager()

