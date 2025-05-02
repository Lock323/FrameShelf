from home.home_list import HomeList
from fastapi import APIRouter, Request, Depends
from content.managers import UserContentManager
from database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from auth.middlewares import auth_guard_exc_true
from fastapi.templating import Jinja2Templates
from fastapi.responses import Response



router = APIRouter(prefix="/home", tags=["home"])


templates = Jinja2Templates("templates")


@router.get('')
async def get_homepage(request: Request, session: AsyncSession = Depends(get_async_session),
                       user=Depends(auth_guard_exc_true)):
    user_content = UserContentManager(session=session, user_id=user.id)
    watchlist = HomeList(session=session, user_content=user_content, status="watchlist")
    watched_list = HomeList(session=session, user_content=user_content, status="watched")
    offset, limit = 0, 5
    watchlist_content = await watchlist.get(offset=offset, limit=limit)
    watched_movie_content = await watched_list.get(offset=offset, limit=limit, media_type="movie")
    watched_tv_content = await watched_list.get(offset=offset, limit=limit, media_type="tv")
    return templates.TemplateResponse("/home/homepage.html", {"request": request, "watchlist_content":
                                        watchlist_content, "watched_movie_content": watched_movie_content,
                                        "watched_tv_content": watched_tv_content, "offset": offset, "limit": limit,
                                        "user": user})


@router.get("/watchlist_items")
async def get_watchlist_items(request: Request, offset: int, limit: int, sort_by: str = None, sorting_order = None,
                              sort_button_id: str = None, session: AsyncSession = Depends(get_async_session),
                              user=Depends(auth_guard_exc_true)):
    offset += limit
    user_content = UserContentManager(session=session, user_id=user.id)
    watchlist = HomeList(session=session, user_content=user_content, status="watchlist")
    watchlist_content = await watchlist.get(offset=offset, limit=limit, sort_by=sort_by, sorting_order=sorting_order)
    if watchlist_content:
        return templates.TemplateResponse("/home/watchlist_items.html", {"request": request, "watchlist_content":
                                            watchlist_content, "offset": offset, "limit": limit, "sort_by": sort_by,
                                            "sorting_order": sorting_order, "sort_button_id": sort_button_id})
    response = Response(status_code=204)
    return response


@router.get("/watchlist_page")
async def get_watchlist_page(request: Request, session: AsyncSession = Depends(get_async_session),
                             user=Depends(auth_guard_exc_true)):
    user_content = UserContentManager(session=session, user_id=user.id)
    watchlist = HomeList(session=session, user_content=user_content, status="watchlist")
    offset, limit = 0, 24
    watchlist_content = await watchlist.get(offset=offset, limit=limit)
    return templates.TemplateResponse("/home/watchlist_page.html", {"request": request, "watchlist_content":
                                        watchlist_content, "offset": offset, "limit": limit})


@router.get("/watchlist_page_items")
async def get_watchlist_page_items(request: Request, offset: int, limit: int,
                                   session: AsyncSession = Depends(get_async_session),
                                   user=Depends(auth_guard_exc_true)):
    offset += limit
    user_content = UserContentManager(session=session, user_id=user.id)
    watchlist = HomeList(session=session, user_content=user_content, status="watchlist")
    watchlist_content = await watchlist.get(offset=offset, limit=limit)
    if watchlist_content:
        return templates.TemplateResponse("/home/watchlist_page_items.html", {"request": request, "watchlist_content":
                                            watchlist_content, "offset": offset, "limit": limit})


@router.get("/watched_movie_items")
async def get_watched_movie_items(request: Request, offset: int, limit: int, sort_by: str = None,
                                  sorting_order: str = None, sort_button_id: str = None,
                                  session: AsyncSession = Depends(get_async_session),
                                  user=Depends(auth_guard_exc_true)):
    offset += limit
    user_content = UserContentManager(session=session, user_id=user.id)
    watched_list = HomeList(session=session, user_content=user_content, status="watched")
    watched_movie_content = await watched_list.get(offset=offset, limit=limit, media_type="movie",
                                                   sorting_order=sorting_order, sort_by=sort_by)
    if watched_movie_content:
        return templates.TemplateResponse("/home/watched_movie_items.html",
                                          {"request": request, "watched_movie_content": watched_movie_content,
                                           "offset": offset, "limit": limit, "sort_by": sort_by,
                                           "sorting_order": sorting_order, "sort_button_id": sort_button_id})
    response = Response(status_code=204)
    return response

@router.get("/watched_movie_page")
async def get_watched_movie_page(request: Request, session: AsyncSession = Depends(get_async_session),
                                 user=Depends(auth_guard_exc_true)):
    user_content = UserContentManager(session=session, user_id=user.id)
    watched_list = HomeList(session=session, user_content=user_content, status="watched")
    offset, limit = 0, 24
    watched_movie_content = await watched_list.get(offset=offset, limit=limit, media_type="movie")
    return templates.TemplateResponse("/home/watched_movie_page.html", {"request": request, "watched_movie_content":
                                        watched_movie_content, "offset": offset, "limit": limit})


@router.get("/watched_movie_page_items")
async def get_watched_movie_page_items(request: Request, offset: int, limit: int, session: AsyncSession =
                                        Depends(get_async_session), user=Depends(auth_guard_exc_true)):
    offset += limit
    user_content = UserContentManager(session=session, user_id=user.id)
    watched_list = HomeList(session=session, user_content=user_content, status="watched")
    watched_movie_content = await watched_list.get(offset=offset, limit=limit, media_type="movie")
    if watched_movie_content:
        return templates.TemplateResponse("/home/watched_movie_page_items.html", {"request": request,
                                            "watched_movie_content": watched_movie_content, "offset": offset,
                                            "limit": limit})


@router.get("/watched_tv_items")
async def get_watched_tv_items(request: Request, offset: int, limit: int, sort_by: str = None,
                               sorting_order: str = None, sort_button_id: str = None,
                               session: AsyncSession = Depends(get_async_session), user=Depends(auth_guard_exc_true)):
    offset += limit
    user_content = UserContentManager(session=session, user_id=user.id)
    watched_list = HomeList(session=session, user_content=user_content, status="watched")
    watched_tv_content = await watched_list.get(offset=offset, limit=limit, media_type="tv",
                                                sorting_order=sorting_order, sort_by=sort_by)
    if watched_tv_content:
        return templates.TemplateResponse("/home/watched_tv_items.html", {"request": request, "watched_tv_content":
                                            watched_tv_content, "offset": offset, "limit": limit, "sort_by": sort_by,
                                            "sorting_order": sorting_order, "sort_button_id": sort_button_id})
    response = Response(status_code=204)
    return response

@router.get("/watched_tv_page")
async def get_watched_tv_page(request: Request, session: AsyncSession = Depends(get_async_session),
                              user=Depends(auth_guard_exc_true)):
    user_content = UserContentManager(session=session, user_id=user.id)
    watched_list = HomeList(session=session, user_content=user_content, status="watched")
    offset, limit = 0, 24
    watched_tv_content = await watched_list.get(offset=offset, limit=limit, media_type="tv")
    return templates.TemplateResponse("/home/watched_tv_page.html", {"request": request, "watched_tv_content":
                                        watched_tv_content, "offset": offset, "limit": limit})


@router.get("/watched_tv_page_items")
async def get_watched_tv_page_items(request: Request, offset: int, limit: int,
                                    session: AsyncSession = Depends(get_async_session),
                                    user=Depends(auth_guard_exc_true)):
    offset += limit
    user_content = UserContentManager(session=session, user_id=user.id)
    watched_list = HomeList(session=session, user_content=user_content, status="watched")
    watched_tv_content = await watched_list.get(offset=offset, limit=limit, media_type="tv")
    if watched_tv_content:
        return templates.TemplateResponse("/home/watched_tv_page_items.html", {"request": request, "watched_tv_content":
                                            watched_tv_content, "offset": offset, "limit": limit})
