from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from auth.middlewares import auth_guard_exc_false
from external_api.client import tmdb_client
from content.data_handlers import search_data_handler
from auth.schemas import UserInfo
from content.schemas import SearchContentSchema


router = APIRouter(prefix="/search", tags=["content", "search"])

templates = Jinja2Templates(directory="templates")

@router.get("/{content_title}")
async def search_content(request: Request, data: SearchContentSchema = Depends(tmdb_client.search_content),
                         user: UserInfo = Depends(auth_guard_exc_false),
                         session: AsyncSession = Depends(get_async_session)):
    data = await search_data_handler.modify_data(data=data.results, session=session, user_data=user)
    return templates.TemplateResponse("search_page.html", {"request": request, "data": data})
