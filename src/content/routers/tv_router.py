from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from content.schemas import SeasonSchema, EpisodeSchema, TVSchema, ButtonsId, TvPageSchema, TvDetailsSchema
from auth.middlewares import auth_guard_exc_true
from content.data_handlers import tv_info_data_handler, content_data_handler
from external_api.client import tmdb_client
from content.managers import TVManager, UserContentManager, SeasonManager, EpisodeManager, ContentManager
from auth.middlewares import auth_guard_exc_false
from auth.schemas import UserInfo

router = APIRouter(prefix="/tv", tags=["content", "tv"])

templates = Jinja2Templates(directory="templates")


@router.get("/page/{content_id}")
async def get_tv_page(request: Request, data: TvPageSchema = Depends(tmdb_client.get_tv_page_data),
                      user: UserInfo = Depends(auth_guard_exc_false),
                      session: AsyncSession = Depends(get_async_session)):
    data = await content_data_handler.modify_tv_page_data(data=data, user_data=user, session=session)
    return templates.TemplateResponse("tv_page.html", {"request": request, "data": data})


@router.get("/info/{tv_id}")
async def get_tv_info(request: Request, buttons_id: str,
                      tv_details: TvDetailsSchema = Depends(tmdb_client.get_tv_details),
                      session: AsyncSession = Depends(get_async_session), user=Depends(auth_guard_exc_true)):
    tv_info_data = await tv_info_data_handler.modify_data(session=session, tv_info_data=tv_details, user_id=user.id)
    return templates.TemplateResponse("tv_module_window.html", {"request": request,
                                                                "tv_data": tv_info_data.model_dump(),
                                                                "buttons_id": buttons_id,
                                                                "watched_percent": tv_info_data.watched_percent})


@router.post("/add_watched")
async def add_tv_to_watched(request: Request, tv_data: TVSchema, buttons_id: ButtonsId,
                            session: AsyncSession = Depends(get_async_session), user=Depends(auth_guard_exc_true)):
    user_content = UserContentManager(session=session, user_id=user.id)
    tv = TVManager(session=session, data=tv_data, user_id=user.id, user_content=user_content)
    await tv.add(status="watched")
    watched_percent = 100
    return templates.TemplateResponse("buttons/tv_module_window/module_tv_in_watched.html",
                                      {"request": request, "tv_data": tv_data.model_dump(),
                                       "buttons_id": buttons_id.buttons_id, "tv_id": tv_data.id,
                                       "watched_percent": watched_percent})


@router.post("/add_season_watched")
async def add_season_to_watched(request: Request, season_data: SeasonSchema, tv_data: TVSchema, buttons_id: ButtonsId,
                                session: AsyncSession = Depends(get_async_session), user=Depends(auth_guard_exc_true)):
    user_content = UserContentManager(session=session, user_id=user.id)
    tv = TVManager(session=session, data=tv_data, user_id=user.id, user_content=user_content)
    season = SeasonManager(session=session, user_content=user_content, data=season_data)
    await season.add(status="watched", tv=tv)
    content_id = await ContentManager.get_id(tmdb_id=tv_data.id, media_type="tv", session=session)
    user_content_id = await user_content.get_id(content_id=content_id)
    watched_percent = await tv_info_data_handler.get_watched_percent(session=session, user_content_id=user_content_id,
                                                                   all_ep=tv_data.number_of_episodes)
    return templates.TemplateResponse("buttons/tv_module_window/season_in_watched.html",
                                      {"request": request, "tv_data": tv_data.model_dump(),
                                       "season": season_data.model_dump(), "buttons_id": buttons_id.buttons_id,
                                       "tv_id": tv_data.id, "watched_percent": watched_percent})

@router.put("/add_episode_watched")
async def add_episode_to_watched(request: Request, season_data: SeasonSchema, episode_data: EpisodeSchema,
                                 tv_data: TVSchema, buttons_id: ButtonsId,
                                 session: AsyncSession = Depends(get_async_session), user=Depends(auth_guard_exc_true)):
    user_content = UserContentManager(session=session, user_id=user.id)
    tv = TVManager(session=session, data=tv_data, user_id=user.id, user_content=user_content)
    episode = EpisodeManager(session=session, user_content=user_content, season=season_data, data=episode_data)
    await episode.add(status="watched", tv=tv)
    content_id = await ContentManager.get_id(tmdb_id=tv_data.id, media_type="tv", session=session)
    user_content_id = await user_content.get_id(content_id=content_id)
    watched_percent = await tv_info_data_handler.get_watched_percent(session=session, user_content_id=user_content_id,
                                                                   all_ep=tv_data.number_of_episodes)
    return templates.TemplateResponse("buttons/tv_module_window/episode_base.html",
                                      {"request": request, "tv_data": tv_data.model_dump(),
                                       "watched_episodes": episode_data.episode_number,
                                       "season": season_data.model_dump(), "buttons_id": buttons_id.buttons_id,
                                       "tv_id": tv_data.id, "watched_percent": watched_percent})

@router.delete("/remove_watched")
async def remove_tv_from_watched(request: Request, tv_data: TVSchema, buttons_id: ButtonsId,
                                 session: AsyncSession = Depends(get_async_session), user=Depends(auth_guard_exc_true)):
    user_content = UserContentManager(session=session, user_id=user.id)
    tv_id = await TVManager.get_id(session=session, media_type="tv", tmdb_id=tv_data.id)
    await user_content.delete(content_id=tv_id)
    watched_percent = 0
    return templates.TemplateResponse("buttons/tv_module_window/module_tv_base.html", {"request": request,
                                       "tv_data": tv_data.model_dump(), "buttons_id": buttons_id.buttons_id,
                                       "tv_id": tv_data.id, "watched_percent": watched_percent})


@router.delete("/remove_season_watched")
async def remove_season_from_watched(request: Request, tv_data: TVSchema, buttons_id: ButtonsId,
                                     season_data: SeasonSchema, session: AsyncSession = Depends(get_async_session),
                                     user = Depends(auth_guard_exc_true)):
    user_content = UserContentManager(session=session, user_id=user.id)
    season = SeasonManager(session=session, user_content=user_content, data=season_data)
    tv_id = await TVManager.get_id(session=session, media_type="tv", tmdb_id=tv_data.id)
    user_content_id = await user_content.get_id(content_id=tv_id)
    await season.delete(user_content_id=user_content_id)
    user_cont_id_after_del: None | int = await user_content.get_id(content_id=tv_id)
    content_id = await ContentManager.get_id(tmdb_id=tv_data.id, media_type="tv", session=session)
    user_content_id = await user_content.get_id(content_id=content_id)
    watched_percent = await tv_info_data_handler.get_watched_percent(session=session, user_content_id=user_content_id,
                                                                     all_ep=tv_data.number_of_episodes)
    return templates.TemplateResponse("buttons/tv_module_window/season_base.html",
                                      {"request": request, "tv_data": tv_data.model_dump(),
                                       "season": season_data.model_dump(), "buttons_id": buttons_id.buttons_id,
                                       "tv_id": tv_data.id, "seasons_left": user_cont_id_after_del,
                                       "watched_percent": watched_percent})


@router.post("/add_watchlist")
async def add_tv_to_watchlist(request: Request, tv_data: TVSchema, buttons_id: ButtonsId,
                              session: AsyncSession = Depends(get_async_session), user=Depends(auth_guard_exc_true)):
    user_content = UserContentManager(session=session, user_id=user.id)
    tv = TVManager(session=session, data=tv_data, user_id=user.id, user_content=user_content)
    await tv.add(status="watchlist")
    return templates.TemplateResponse("buttons/tv_in_watchlist.html",
                                      {"request": request, "tv_data": tv_data.model_dump(), "tv_id": tv_data.id,
                                       "buttons_id": buttons_id.buttons_id})


@router.delete("/remove_watchlist")
async def remove_tv_from_watchlist(request: Request, tv_data: TVSchema, buttons_id: ButtonsId,
                                   session: AsyncSession = Depends(get_async_session),
                                   user=Depends(auth_guard_exc_true)):
    user_content = UserContentManager(session=session, user_id=user.id)
    tv_id = await TVManager.get_id(session=session, media_type="tv", tmdb_id=tv_data.id)
    await user_content.delete(content_id=tv_id)
    return templates.TemplateResponse("buttons/tv_base.html", {"request": request, "tv_data": tv_data.model_dump(),
                                       "buttons_id": buttons_id.buttons_id, "tv_id": tv_data.id})
