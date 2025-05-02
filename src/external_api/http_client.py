import json
import aiohttp
import redis
from content.schemas import SearchContentSchema, TvPageSchema, TvDetailsSchema, MoviePageSchema, IndexSchema
from config import settings
import base64


rd = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, password=settings.REDIS_PASSWORD)


class HTTPClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.proxy = settings.proxy_url
        self.api_key = settings.API_KEY
        self.client = None
        self.connector = None

    async def open_session(self):
            self.connector = aiohttp.TCPConnector(
                limit=50, keepalive_timeout=90)
            self.client = aiohttp.ClientSession(base_url=self.base_url, connector=self.connector)


    async def close_session(self):
        await self.client.close()

    async def search_content(self, content_title):
        async with self.client.get('/3/search/multi',
                                   proxy=self.proxy,
                                   params={"query": content_title, "api_key": self.api_key}) as response:
            data = await response.json()
            return SearchContentSchema.model_validate(data)

    async def get_movie_page_data(self, content_id: str) -> MoviePageSchema:
        details = await self.get_movie_details(movie_id=content_id)
        credits = await self.get_movie_credits(movie_id=content_id)
        recommendations = await self.get_movie_recommendations(movie_id=content_id)
        movie_page_data = {"details": details, "credits": credits, "recommendations": recommendations}
        return MoviePageSchema.model_validate(movie_page_data)

    async def get_tv_page_data(self, content_id: str) -> TvPageSchema:
        details = await self.get_tv_details(tv_id=content_id)
        credits = await self.get_tv_credits(tv_id=content_id)
        recommendations = await self.get_tv_recommendations(tv_id=content_id)
        tv_page_data = {"details": details, "credits": credits, "recommendations": recommendations}
        return TvPageSchema.model_validate(tv_page_data)

    async def get_tv_details(self, tv_id):
        async with self.client.get(f'/3/tv/{tv_id}',
                                   proxy=self.proxy,
                                   params={"api_key": self.api_key}) as response:
            data = await response.json()
            return TvDetailsSchema.model_validate(data)

    async def get_movie_details(self, movie_id):
        async with self.client.get(f"/3/movie/{movie_id}",
                                   proxy=self.proxy,
                                   params={"api_key": self.api_key}) as response:
            data = await response.json()
            return data

    async def get_tv_credits(self, tv_id):
        async with self.client.get(f"/3/tv/{tv_id}/credits",
                                   proxy=self.proxy,
                                   params={"api_key": self.api_key}) as response:
            data = await response.json()
            return data

    async def get_movie_credits(self, movie_id):
        async with self.client.get(f"/3/movie/{movie_id}/credits",
                                   proxy=self.proxy,
                                   params={"api_key": self.api_key}) as response:
            data = await response.json()
            return data

    async def get_tv_recommendations(self, tv_id):
        async with self.client.get(f"/3/tv/{tv_id}/recommendations",
                                   proxy=self.proxy,
                                   params={"api_key": self.api_key}) as response:
            data = await response.json()
            return data

    async def get_movie_recommendations(self, movie_id):
        async with self.client.get(f"/3/movie/{movie_id}/recommendations",
                                   proxy=self.proxy,
                                   params={"api_key": self.api_key}) as response:
            data = await response.json()
            return data

    async def get_index_data(self):
        cache_data = rd.get("main_page_data")
        if cache_data:
            return cache_data
        popular_movies = await self.get_popular_movies()
        upcoming_movies = await self.get_upcoming_movies()
        popular_tv = await self.get_popular_tv()
        airing_today_tv = await self.get_airing_today_tv()
        rd.set("main_page_data", json.dumps({"popular_movies": popular_movies, "upcoming_movies": upcoming_movies,
                "popular_tv": popular_tv, "airing_today_tv": airing_today_tv}))
        rd.expire("main_page_data", 86400)
        main_page_data = {"popular_movies": popular_movies, "upcoming_movies": upcoming_movies,
                "popular_tv": popular_tv, "airing_today_tv": airing_today_tv}
        return IndexSchema.model_validate(main_page_data)

    async def get_popular_movies(self):
        async with self.client.get(f"/3/movie/popular",
                                   proxy=self.proxy,
                                   params={"api_key": self.api_key}) as response:
            data = await response.json()
            return data

    async def get_upcoming_movies(self):
        async with self.client.get(f"/3/movie/upcoming",
                                   proxy=self.proxy,
                                   params={"api_key": self.api_key}) as response:
            data = await response.json()
            return data

    async def get_popular_tv(self):
        async with self.client.get(f"/3/tv/popular",
                                   proxy=self.proxy,
                                   params={"api_key": self.api_key}) as response:
            data = await response.json()
            return data

    async def get_airing_today_tv(self):
        async with self.client.get(f"/3/tv/airing_today",
                                   proxy=self.proxy,
                                   params={"api_key": self.api_key}) as response:
            data = await response.json()
            return data


class ImageHTTPClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.proxy = settings.proxy_url
        self.client = None
        self.connector = None

    async def open_session(self):
            self.connector = aiohttp.TCPConnector(
                limit=50, keepalive_timeout=90)
            self.client = aiohttp.ClientSession(base_url=self.base_url, connector=self.connector)

    async def close_session(self):
        await self.client.close()

    async def get_image(self, size: str, poster_path: str) -> dict:
        async with self.client.get(f"/t/p/{size}/{poster_path}",
                                   proxy=self.proxy,
                                    ) as response:
            image_data = await response.read()
            content_type = response.headers.get('Content-Type', 'image/jpeg')
            return {"image_data": image_data, "content_type": content_type}

    async def get_main_page_image(self, size: str, poster_path: str):
        cache_data = rd.get(f"{poster_path}")
        if cache_data:
            poster_data = json.loads(cache_data)
            poster_data["image_data"] = base64.b64decode(poster_data["image_data"])
            return poster_data
        poster_data = await self.get_image(size, poster_path)
        poster_data["image_data"] = base64.b64encode(poster_data["image_data"]).decode("utf-8")
        rd.set(f"{poster_path}", json.dumps(poster_data))
        rd.expire(f"{poster_path}", 86400)
        poster_data["image_data"] = base64.b64decode(poster_data["image_data"])
        return poster_data
