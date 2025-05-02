from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from content.managers import UserContentManager
from content.schemas import MovieSchema, TVSchema
from content.models import ContentTable, UserContentTable
from content.data_handlers import DataHandler
from typing import Sequence

home_content_data_handler = DataHandler()

class HomeList:

    def __init__(self, session: AsyncSession, user_content: UserContentManager, status: str):
        self.session = session
        self.user_content = user_content
        self.status = status

    async def get(self, offset, limit, media_type=None, sort_by: str = None, sorting_order: str = None) \
            -> list[dict] | None:
        content_list = []
        content_models = await self.get_part(user_id=self.user_content.user_id, offset=offset, limit=limit,
                                             media_type=media_type, sort_by=sort_by, sorting_order=sorting_order)
        if content_models:
            for content_model in content_models:
                content = await self.modify_content_model(content_model=content_model,
                                                          session=self.session,
                                                          user_id=self.user_content.user_id,
                                                          user_content=self.user_content)
                content_list.append(content)
            return content_list

    async def get_part(self, user_id: int, offset: int, limit: int, media_type: str, sort_by=None, sorting_order=None) \
            -> Sequence[ContentTable] | Sequence[None]:
        order_by = self.get_order(sort_by, sorting_order)
        if media_type:
            stmt = select(ContentTable).join(
                UserContentTable, ContentTable.id == UserContentTable.content_id).where(
                (UserContentTable.users_id == user_id) & (UserContentTable.status == self.status)
                & (ContentTable.media_type == media_type)).order_by(order_by).offset(offset).limit(limit)
        else:
            stmt = select(ContentTable).join(
                UserContentTable, ContentTable.id == UserContentTable.content_id).where(
                (UserContentTable.users_id == user_id) & (UserContentTable.status == self.status)).order_by(
                order_by).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        result = result.scalars().all()
        return result

    def get_order(self, sort_by: str = None, sorting_order: str = None):
        order_by = UserContentTable.added_at.desc()
        if sort_by is None and sorting_order is None:
            return order_by
        if sort_by == "release_date" and sorting_order == "asc":
            order_by = ContentTable.release_date.asc()
        elif sort_by == "release_date" and sorting_order == "desc":
            order_by = ContentTable.release_date.desc()
        elif sort_by == "rating" and sorting_order == "asc":
            order_by = ContentTable.vote_average.asc()
        elif sort_by == "rating" and sorting_order == "desc":
            order_by = ContentTable.vote_average.desc()
        elif sort_by == "added_time" and sorting_order == "asc":
            order_by = UserContentTable.added_at.asc()
        elif sort_by == "added_time" and sorting_order == "desc":
            order_by = UserContentTable.added_at.desc()
        return order_by

    async def modify_content_model(self, content_model: ContentTable, session: AsyncSession, user_id: int,
                                   user_content: UserContentManager) -> dict | None:
        content_dict = content_model.__dict__
        content_dict["media_type"] = content_dict["media_type"].value
        content_dict["id"] = content_dict["tmdb_id"]
        if content_model.media_type == "movie":
            content = MovieSchema.model_validate(content_dict)
            await home_content_data_handler.add_buttons(session=session, user_content=user_content,
                                                        user_id=user_id,
                                                        content=content)
            return content.model_dump()
        elif content_model.media_type == "tv":
            content_dict["name"] = content_dict["title"]
            content_dict["first_air_date"] = content_dict["release_date"]
            content = TVSchema.model_validate(content_dict)
            await home_content_data_handler.add_buttons(session=session, user_content=user_content,
                                                        user_id=user_id,
                                                        content=content)
            return content.model_dump()
