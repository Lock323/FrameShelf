from content.models import ContentTable, UserContentTable, SeasonEpisodeTable
from sqlalchemy import select, delete, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from content.schemas import MovieSchema, TVSchema, SeasonSchema, EpisodeSchema
from abc import ABC, abstractmethod


class UserContentManager:

    def __init__(self, session: AsyncSession, user_id: int):
        self.session = session
        self.user_id = user_id

    async def insert(self, status, content_id):
        try:
            user_content = UserContentTable(
                users_id=self.user_id,
                content_id=content_id,
                status=status
            )
            self.session.add(user_content)
            await self.session.flush()
            return user_content.id
        except IntegrityError:
            await self.session.rollback()
            existing_status = await self.get_status(content_id=content_id)
            if status == "watched" and existing_status == "watched":
                user_content_id = await self.get_id(content_id=content_id)
            else:
                await self.delete(content_id=content_id)
                user_content_id = await self.insert(status=status, content_id=content_id)
            return user_content_id

    async def get_status(self, content_id) -> str:
        statement = select(UserContentTable.status).where(
            (self.user_id == UserContentTable.users_id) & (content_id == UserContentTable.content_id))
        status = await self.session.execute(statement)
        status = status.scalar_one_or_none()
        status = status.value if status else None
        return status

    async def get_id(self, content_id):
        statement = select(UserContentTable.id).where(
            (self.user_id == UserContentTable.users_id) & (content_id == UserContentTable.content_id))
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def delete(self, content_id):
        stmt = delete(UserContentTable).where((UserContentTable.content_id == content_id) &
                                              (UserContentTable.users_id == self.user_id))
        await self.session.execute(stmt)
        await self.session.commit()


class ContentManager(ABC):

    def __init__(self, session: AsyncSession, data: TVSchema | MovieSchema):
        self.session = session
        self.data = data

    @abstractmethod
    async def add(self, status: str):
        pass

    @abstractmethod
    async def insert(self):
        pass

    @staticmethod
    async def get(session: AsyncSession, content_id: int) -> ContentTable | None:
        stmt = select(ContentTable).where(ContentTable.id == content_id)
        content = await session.execute(stmt)
        return content.scalar_one_or_none()

    @staticmethod
    async def get_id(tmdb_id, media_type: str, session: AsyncSession) -> int | None:
        statement = select(ContentTable.id).where(
            (tmdb_id == ContentTable.tmdb_id) & (media_type == ContentTable.media_type))
        content_id = await session.execute(statement)
        return content_id.scalar_one_or_none()


class MovieManager(ContentManager):
    def __init__(self, session: AsyncSession, data: MovieSchema, user_id: int, user_content: UserContentManager):
        super().__init__(session=session, data=data)
        self.user_id = user_id
        self.user_content = user_content

    async def add(self, status: str):
        content_id = await self.insert()
        await self.user_content.insert(content_id=content_id, status=status)
        await self.session.commit()

    async def insert(self):
        try:
            content = ContentTable(
                tmdb_id=self.data.id,
                media_type=self.data.media_type,
                title=self.data.title,
                release_date=self.data.release_date,
                poster_path=self.data.poster_path,
                vote_average=self.data.vote_average)
            self.session.add(content)
            await self.session.flush()
            return content.id
        except IntegrityError:
            await self.session.rollback()
            content_id = await self.get_id(tmdb_id=self.data.id, media_type="movie", session=self.session)
            return content_id


class TVManager(ContentManager):

    def __init__(self, session: AsyncSession, data: TVSchema, user_id: int, user_content: UserContentManager):
        super().__init__(session=session, data=data)
        self.user_id = user_id
        self.user_content = user_content

    async def add(self, status: str):
        content_id = await self.insert()
        user_content_id = await self.user_content.insert(content_id=content_id, status=status)
        if status == "watched":
            for season in self.data.seasons:
                season = SeasonManager(data=season, session=self.session, user_content=self.user_content)
                await season.insert(user_content_id=user_content_id)
        await self.session.commit()

    async def insert(self):
        try:
            content = ContentTable(
                tmdb_id=self.data.id,
                media_type=self.data.media_type,
                title=self.data.name,
                release_date=self.data.first_air_date,
                poster_path=self.data.poster_path,
                vote_average=self.data.vote_average)
            self.session.add(content)
            await self.session.flush()
            return content.id
        except IntegrityError:
            await self.session.rollback()
            content_id = await self.get_id(tmdb_id=self.data.id, media_type="tv", session=self.session)
            return content_id


class SeasonEpisodeManager(ABC):

    def __init__(self, session: AsyncSession, data: SeasonSchema | EpisodeSchema):
        self.session = session
        self.data = data

    @staticmethod
    async def get_watched_ep_for_tv(session: AsyncSession, user_content_id):
        stmt = select(SeasonEpisodeTable.watched_episodes).filter_by(user_content_id=user_content_id)
        result = await session.execute(stmt)
        result = result.fetchall()
        return result

    @abstractmethod
    async def add(self, status: str, tv: TVManager):
        pass

    @abstractmethod
    async def insert(self, user_content_id):
        pass

    @abstractmethod
    async def update(self, user_content_id):
        pass


class SeasonManager(SeasonEpisodeManager):
    def __init__(self, data: SeasonSchema, session: AsyncSession, user_content: UserContentManager):
        super().__init__(data=data, session=session)
        self.user_content = user_content


    async def add(self, status: str, tv: TVManager):
        content_id = await tv.insert()
        user_content_id = await self.user_content.insert(status=status, content_id=content_id)
        await self.insert(user_content_id=user_content_id)
        await self.session.commit()

    async def insert(self, user_content_id):
        try:
            season_episode = SeasonEpisodeTable(
                user_content_id=user_content_id,
                season_number=self.data.season_number,
                season_name=self.data.name,
                watched_episodes=self.data.episode_count
            )
            self.session.add(season_episode)
            await self.session.flush()
            return season_episode.id
        except IntegrityError:
            await self.session.rollback()
            await self.update(user_content_id=user_content_id)

    async def update(self, user_content_id):
        stmt = update(SeasonEpisodeTable).values({"watched_episodes": self.data.episode_count}).where(
            (SeasonEpisodeTable.user_content_id == user_content_id) &
            (SeasonEpisodeTable.season_number == self.data.season_number))
        await self.session.execute(stmt)
        await self.session.flush()

    async def get_id(self, user_content_id):
        stmt = select(SeasonEpisodeTable.id).where(
            (SeasonEpisodeTable.user_content_id == user_content_id) & (
                        SeasonEpisodeTable.season_number == self.data.season_number))
        seasons_episodes_id = await self.session.execute(stmt)
        return seasons_episodes_id.scalar_one_or_none()

    async def delete(self, user_content_id):
        season_episode_id = await self.get_id(user_content_id=user_content_id)
        if season_episode_id:
            season_episode = await self.session.get(SeasonEpisodeTable, season_episode_id)
            await self.session.delete(season_episode)
            await self.delete_user_content_if_not_season(user_content_id=user_content_id)
            await self.session.commit()

    async def delete_user_content_if_not_season(self, user_content_id):
        stmt = select(func.count()).select_from(SeasonEpisodeTable).filter_by(user_content_id=user_content_id)
        result = await self.session.execute(stmt)
        count = result.scalar()
        if count == 0:
            stmt = delete(UserContentTable).where(UserContentTable.id == user_content_id)
            await self.session.execute(stmt)

    async def get_watched_ep_for_season(self, user_content_id):
        stmt = select(SeasonEpisodeTable.watched_episodes).filter_by(
            user_content_id=user_content_id, season_number=self.data.season_number)
        result = await self.session.execute(stmt)
        result = result.scalar()
        return result


class EpisodeManager(SeasonEpisodeManager):

    def __init__(self, data: EpisodeSchema, session: AsyncSession, user_content: UserContentManager,
                 season: SeasonSchema):
        super().__init__(data=data, session=session)
        self.user_content = user_content
        self.season = season

    async def add(self, status: str, tv: TVManager):
        content_id = await tv.insert()
        user_content_id = await self.user_content.insert(content_id=content_id, status=status)
        await self.insert(user_content_id=user_content_id)
        await self.session.commit()

    async def insert(self, user_content_id):
        try:
            season_episode = SeasonEpisodeTable(
                user_content_id=user_content_id,
                season_number=self.season.season_number,
                season_name=self.season.name,
                watched_episodes=self.data.episode_number
            )
            self.session.add(season_episode)
            await self.session.flush()
            return season_episode.id
        except IntegrityError:
            await self.session.rollback()
            await self.update(user_content_id=user_content_id)

    async def update(self, user_content_id):
        stmt = update(SeasonEpisodeTable).values({"watched_episodes": self.data.episode_number}).where(
            (SeasonEpisodeTable.user_content_id == user_content_id) &
            (SeasonEpisodeTable.season_number == self.season.season_number))
        await self.session.execute(stmt)
        await self.session.flush()