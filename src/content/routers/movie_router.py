from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from content.schemas import MovieSchema, MoviePageSchema
from auth.middlewares import auth_guard_exc_true
from content.managers import MovieManager, UserContentManager
from content.data_handlers import content_data_handler
from external_api.client import tmdb_client
from auth.middlewares import auth_guard_exc_false
from auth.schemas import UserInfo

router = APIRouter(prefix="/movie", tags=["content", "movie"])

templates = Jinja2Templates(directory="templates")
buttons_templates = Jinja2Templates(directory="templates/buttons")


@router.get("/page/{content_id}")
async def get_movie_page(request: Request, data: MoviePageSchema = Depends(tmdb_client.get_movie_page_data),
                         user: UserInfo = Depends(auth_guard_exc_false),
                         session: AsyncSession = Depends(get_async_session)):
    data = await content_data_handler.modify_movie_page_data(data=data, session=session, user_data=user)
    return templates.TemplateResponse("movie_page.html", {"request": request, "data": data})


@router.post("/status")
async def update_movie_status(request: Request, movie_data: MovieSchema, user=Depends(auth_guard_exc_true),
                              session: AsyncSession = Depends(get_async_session)):
    status = request.headers["status"]
    user_content = UserContentManager(session=session, user_id=user.id)
    movie_manager = MovieManager(session=session, user_content=user_content, data=movie_data, user_id=user.id)
    await movie_manager.add(status=status)
    if status == "watched":
        return buttons_templates.TemplateResponse("movie_in_watched.html", {"request": request,
                                                                            "content": movie_data.model_dump()})
    elif status == "watchlist":
        return buttons_templates.TemplateResponse("movie_in_watchlist.html", {"request": request,
                                                                              "content": movie_data.model_dump()})


@router.delete("/remove")
async def remove_movie_from_list(request: Request, movie_data: MovieSchema,
                                 session: AsyncSession = Depends(get_async_session), user=Depends(auth_guard_exc_true)):
    user_content = UserContentManager(session=session, user_id=user.id)
    movie_id = await MovieManager.get_id(session=session, tmdb_id=movie_data.id, media_type=movie_data.media_type)
    await user_content.delete(content_id=movie_id)
    return buttons_templates.TemplateResponse("movie_base.html", {"request": request,
                                                                  "content": movie_data.model_dump()})
