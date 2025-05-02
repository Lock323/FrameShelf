from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import PlainTextResponse
from database import get_async_session
from auth.schemas import UserCreate, UserLogin, ResetPasswordData
from auth.manager import user_manager
from auth.jwt_handler import access_token_manager, reset_pw_token_manager
from tasks.tasks import send_email_reset_pw_link
from exceptions import InvalidResetPWTokenError

router = APIRouter(tags=["auth"])

templates = Jinja2Templates(directory="templates")


@router.get("/sign_up")
async def get_sign_up_page(request: Request):
    return templates.TemplateResponse("sign_up.html", {"request": request})

@router.get("/log_in")
async def get_log_in_page(request: Request):
    referer = request.headers.get("referer")
    return templates.TemplateResponse("log_in.html", {"request": request, "referer": referer})


@router.post("/sign_up")
async def create_user(user_data: UserCreate, session: AsyncSession = Depends(get_async_session)):
    return await user_manager.create_user(user_data=user_data, session=session,
                                          token_manager=access_token_manager)


@router.post("/log_in")
async def authenticate_user(user_data: UserLogin, session: AsyncSession = Depends(get_async_session)):
    response = await user_manager.login_user(user_data=user_data, session=session,
                                             token_manager=access_token_manager, referer=user_data.referer)
    return response

@router.get("/email_reset_pw")
async def get_email_to_reset_pw(request: Request):
    return templates.TemplateResponse("email_for_reset_pw.html", {"request": request})

@router.get("/link_reset_pw")
async def send_link_to_reset_pw(user_email: str, session: AsyncSession = Depends(get_async_session)):
    user = await user_manager.get_by_email(user_email=user_email, session=session)
    if user:
        reset_pw_token = reset_pw_token_manager.sign_token(user_id=user.id, user_hashed_pw=user.hashed_password)
        send_email_reset_pw_link.delay(token=reset_pw_token, user_email=user_email)
        return PlainTextResponse("Link to reset password sent to your e-mail", status_code=200)
    else:
        return PlainTextResponse("No account connected to this e-mail", status_code=400)

@router.get("/reset_pw/{reset_pw_token}")
async def get_reset_pw_page(reset_pw_token, user_email: str, request: Request,
                            session: AsyncSession = Depends(get_async_session)):
    user = await user_manager.get_by_email(user_email=user_email, session=session)
    if user:
        decoded_reset_pw_token = reset_pw_token_manager.decode_token(token=reset_pw_token,
                                                                     user_hashed_pw=user.hashed_password)
        if decoded_reset_pw_token:
            return templates.TemplateResponse("reset_pw.html", {"request": request, "user_email": user_email,
                                                                "reset_pw_token": reset_pw_token})
        else:
            raise InvalidResetPWTokenError

@router.put("/reset_pw")
async def reset_pw(reset_pw_data: ResetPasswordData, session: AsyncSession = Depends(get_async_session)):
    user = await user_manager.get_by_email(user_email=reset_pw_data.user_email, session=session)
    if user:
        decoded_reset_pw_token = reset_pw_token_manager.decode_token(token=reset_pw_data.reset_pw_token,
                                                                     user_hashed_pw=user.hashed_password)
        if decoded_reset_pw_token:
            await user_manager.reset_password(session=session, new_password=reset_pw_data.new_password,
                                              user_email=reset_pw_data.user_email)
            return PlainTextResponse("Password has been changed successfully", status_code=200)
        else:
            raise InvalidResetPWTokenError
    else:
        return PlainTextResponse("No account connected to this e-mail", status_code=400)

