from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.params import Depends
from auth.schemas import UserInfo
from auth.middlewares import auth_guard_exc_false
from content.data_handlers import index_data_handler
from auth.router import router as auth_router
from exception_handlers import valid_exc_handler, login_token_exc_handler, reset_pw_token_exc_handler
from external_api.client import tmdb_client, image_tmdb_client
from exceptions import InvalidLoginTokenError, InvalidResetPWTokenError
from content.routers.search_router import router as search_router
from content.routers.movie_router import router as movie_router
from content.routers.tv_router import router as tv_router
from proxy.router import router as proxy_router
from starlette.templating import Jinja2Templates
from home.home_router import router as home_router
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from content.schemas import IndexSchema


@asynccontextmanager
async def lifespan(app: FastAPI):
    await tmdb_client.open_session()
    await image_tmdb_client.open_session()
    yield
    await tmdb_client.close_session()
    await image_tmdb_client.close_session()


app = FastAPI(
    title="FrameShelf",
    lifespan=lifespan)


templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index(request: Request, data: IndexSchema = Depends(tmdb_client.get_index_data), user: UserInfo =
                        Depends(auth_guard_exc_false), session: AsyncSession = Depends(get_async_session)):
    data = await index_data_handler.modify_data(data=data, session=session, user_data=user)
    return templates.TemplateResponse("index.html", {"request": request, "data": data, "user": user})


app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(search_router)
app.include_router(movie_router)
app.include_router(tv_router)
app.include_router(home_router)
app.include_router(auth_router)
app.include_router(proxy_router)
app.add_exception_handler(RequestValidationError, valid_exc_handler)
app.add_exception_handler(InvalidLoginTokenError, login_token_exc_handler)
app.add_exception_handler(InvalidResetPWTokenError, reset_pw_token_exc_handler)
