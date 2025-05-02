from content.managers import ContentManager
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from content.managers import TVManager, UserContentManager, SeasonManager, SeasonEpisodeManager
from content.schemas import TvPageSchema, MovieSchema, TvDetailsSchema, CastPersonSchema, MoviePageSchema, IndexSchema, \
    CrewPersonSchema
import json
from content.schemas import TVSchema
from auth.schemas import UserInfo

templates = Jinja2Templates("templates")


class DataHandler:
    movie_base = templates.get_template("buttons/movie_base.html")
    movie_in_watched = templates.get_template("buttons/movie_in_watched.html")
    movie_in_watchlist = templates.get_template("buttons/movie_in_watchlist.html")
    tv_base = templates.get_template("buttons/tv_base.html")
    tv_in_watched = templates.get_template("buttons/tv_in_watched.html")
    tv_in_watchlist = templates.get_template("buttons/tv_in_watchlist.html")
    module_tv_base = templates.get_template("buttons/tv_module_window/module_tv_base.html")
    module_tv_in_watched = templates.get_template("buttons/tv_module_window/module_tv_in_watched.html")
    season_in_watched = templates.get_template("buttons/tv_module_window/season_in_watched.html")
    season_base = templates.get_template("buttons/tv_module_window/season_base.html")

    async def add_buttons(self, content: MovieSchema | TVSchema, user_id: int, session: AsyncSession,
                          user_content: UserContentManager):
        content_id = await ContentManager.get_id(tmdb_id=content.id, media_type=content.media_type, session=session)
        status = None
        if user_id:
            status = await user_content.get_status(content_id=content_id)
        buttons_id = "content" + str(content.id)
        if content.media_type == "movie":
            if status == "watched":
                content.buttons = self.movie_in_watched.render(content=content.model_dump())
            elif status == "watchlist":
                content.buttons = self.movie_in_watchlist.render(content=content.model_dump())
            else:
                content.buttons = self.movie_base.render(content=content.model_dump())
        elif content.media_type == "tv":
            if status == "watched":
                content.buttons = self.tv_in_watched.render(tv_data=content.model_dump(), tv_id=content.id,
                                                            buttons_id=buttons_id)
            elif status == "watchlist":
                content.buttons = self.tv_in_watchlist.render(tv_data=content.model_dump(), tv_id=content.id,
                                                              buttons_id=buttons_id)
            else:
                content.buttons = self.tv_base.render(tv_data=content.model_dump(), tv_id=content.id,
                                                      buttons_id=buttons_id)
        return content

class SearchDataHandler(DataHandler):

    async def modify_data(self, data: list[MovieSchema | TVSchema], session: AsyncSession,
                          user_data: UserInfo = None) -> list[MovieSchema | TVSchema]:
        user_id = user_data.id if user_data else None
        user_content = UserContentManager(session=session, user_id=user_id)
        modified_data = []
        allowed_media_types = ["movie", "tv"]
        for content in data:
            if content.media_type in allowed_media_types:
                content = await self.add_buttons(content=content, user_id=user_id, session=session,
                                                 user_content=user_content)
                modified_data.append(content)
        modified_data = sorted(modified_data, key=lambda content: content.popularity, reverse=True)
        return modified_data



class TvInfoDataHandler:

    async def modify_data(self, tv_info_data: TvDetailsSchema, session: AsyncSession, user_id: int) -> TvDetailsSchema:
        user_content = UserContentManager(session=session, user_id=user_id)
        tv_data = TVSchema.model_validate(tv_info_data.model_dump())
        tv = TVManager(session=session, user_id=user_id, user_content=user_content, data=tv_data)
        content_id = await tv.get_id(session=tv.session, tmdb_id=tv.data.id, media_type="tv")
        user_content_id = await user_content.get_id(content_id=content_id)
        tv_info_data = await self.set_watched(tv_info_data=tv_info_data, tv=tv, user_content=user_content,
                                              content_id=content_id, user_content_id=user_content_id)
        tv_info_data.watched_percent = await self.get_watched_percent(user_content_id=user_content_id,
                                                                      all_ep=tv_info_data.number_of_episodes,
                                                                      session=session)
        return tv_info_data

    async def set_watched(self, tv_info_data: TvDetailsSchema, tv: TVManager, user_content: UserContentManager, content_id: int,
                          user_content_id: int) -> TvDetailsSchema:
        status = await user_content.get_status(content_id=content_id)
        if status == "watched":
            tv_info_data.watched = True
        else:
            tv_info_data.watched = False
        new_seasons = []
        for season_data in tv_info_data.seasons:
            if season_data.name == "Specials":
                continue
            season = SeasonManager(session=tv.session, user_content=user_content, data=season_data)
            seasons_episodes_id = await season.get_id(user_content_id=user_content_id)
            if seasons_episodes_id:
                season_data.watched = True
            else:
                season_data.watched = False
            watched_episodes = await season.get_watched_ep_for_season(user_content_id=user_content_id)
            season_data.watched_episodes = watched_episodes
            new_seasons.append(season_data)
        tv_info_data.seasons = new_seasons
        return tv_info_data

    async def get_watched_percent(self, user_content_id: int, all_ep: int, session: AsyncSession) -> int:
        watched_ep = 0
        result = await SeasonEpisodeManager.get_watched_ep_for_tv(user_content_id=user_content_id, session=session)
        for i in result:
            watched_ep += i[0]
        try:
            watched_percent = watched_ep / all_ep * 100
        except ZeroDivisionError:
            watched_percent = 0
        return round(watched_percent, 1)



class ContentPageDataHandler(DataHandler):

    async def modify_movie_page_data(self, data: MoviePageSchema, user_data: UserInfo, session: AsyncSession) \
            -> dict | None:
        if data:
            user_id = user_data.id if user_data else None
            user_content = UserContentManager(session=session, user_id=user_id)
            movie_page_data = data.details.model_dump()
            movie_page_data["media_type"] = "movie"
            movie_page_data = MovieSchema.model_validate(movie_page_data)
            await self.add_buttons(content=movie_page_data, session=session, user_content=user_content,
                                   user_id=user_id)
            movie_page_data = movie_page_data.model_dump()
            movie_page_data["genres"] = []
            for genre in data.details.genres:
                movie_page_data["genres"].append(genre.name)
            self.add_crew_member(crew=data.credits.crew, content_page_data=movie_page_data, media_type="movie")
            self.add_cast_member(cast=data.credits.cast, content_page_data=movie_page_data)
            await self.add_recommend_content(recommend_list=data.recommendations.results, session=session,
                                       content_page_data=movie_page_data, user_content=user_content, user_id=user_id)
            return movie_page_data

    async def modify_tv_page_data(self, data: TvPageSchema, session: AsyncSession, user_data: UserInfo) -> dict | None:
        if data:
            user_id = user_data.id if user_data else None
            user_content = UserContentManager(session=session, user_id=user_id)
            tv_page_data = data.details.model_dump()
            tv_page_data["media_type"] = "tv"
            tv_page_data = TVSchema.model_validate(tv_page_data)
            await self.add_buttons(content=tv_page_data, user_id=user_id, session=session,
                                   user_content=user_content)
            tv_page_data = tv_page_data.model_dump()
            tv_page_data["genres"] = []
            for genre in data.details.genres:
                tv_page_data["genres"].append(genre.name)
            self.add_crew_member(crew=data.credits.crew, content_page_data=tv_page_data, media_type="tv")
            self.add_cast_member(cast=data.credits.cast, content_page_data=tv_page_data)
            await self.add_recommend_content(recommend_list=data.recommendations.results, session=session,
                                             content_page_data=tv_page_data, user_content=user_content,
                                             user_id=user_id)
            return tv_page_data
        else:
            return None

    def add_crew_member(self, crew: list[CrewPersonSchema], content_page_data: dict, media_type: str):
        if media_type == "movie":
            for crew_member in crew:
                if crew_member.job == "Director":
                    content_page_data["director"] = crew_member.name
                if crew_member.job == "Writer":
                    content_page_data["writer"] = crew_member.name
        elif media_type == "tv":
            content_page_data["creators"] = []
            for crew_member in crew:
                if crew_member.job == "Executive Producer":
                    content_page_data["creators"].append(crew_member.name)

    def add_cast_member(self, cast: list[CastPersonSchema], content_page_data: dict):
        content_page_data["cast"] = []
        for cast_member in cast:
            if cast_member.order < 10:
                actor = {"name": cast_member.name, "profile_path": cast_member.profile_path,
                         "character": cast_member.character}
                content_page_data["cast"].append(actor)

    async def add_recommend_content(self, recommend_list: list[TVSchema | MovieSchema], session: AsyncSession,
                                    content_page_data: dict, user_content: UserContentManager, user_id: int):
        content_page_data["recommendations"] = []
        counter = 0
        for recommend_content in recommend_list:
            if counter < 11:
                await self.add_buttons(content=recommend_content, session=session, user_id=user_id,
                                       user_content=user_content)
                content_page_data["recommendations"].append(recommend_content)
                counter += 1


class MainPageDataHandler(DataHandler):

    async def modify_data(self, data: IndexSchema | bytes, user_data: UserInfo, session: AsyncSession):
        if data:
            if type(data) is bytes:
                data = self.modify_cache_data(data)
            user_id = user_data.id if user_data else None
            user_content = UserContentManager(session=session, user_id=user_id)
            for movie in data.popular_movies.results:
                movie.media_type = "movie"
                await self.add_buttons(content=movie, user_id=user_id, session=session,
                                       user_content=user_content)
            for movie in data.upcoming_movies.results:
                movie.media_type = "movie"
                await self.add_buttons(content=movie, user_id=user_id, session=session,
                                       user_content=user_content)
            for tv in data.popular_tv.results:
                tv.media_type = "tv"
                await self.add_buttons(content=tv, user_id=user_id, session=session,
                                       user_content=user_content)
            for tv in data.airing_today_tv.results:
                tv.media_type = "tv"
                await self.add_buttons(content=tv, user_id=user_id, session=session,
                                       user_content=user_content)
            data = data.model_dump()
            return data

    def modify_cache_data(self, data):
        data = json.loads(data)
        data = IndexSchema.model_validate(data)
        return data



tv_info_data_handler = TvInfoDataHandler()
search_data_handler = SearchDataHandler()
content_data_handler = ContentPageDataHandler()
index_data_handler = MainPageDataHandler()
