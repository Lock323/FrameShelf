from pydantic import BaseModel, field_validator
from typing import Optional


class MovieSchema(BaseModel):
    id: int
    media_type: Optional[str] = None
    title: Optional[str] = None
    release_date: Optional[str] = None
    poster_path: Optional[str] = None
    vote_average: Optional[float] = None
    buttons: Optional[str] = None
    popularity: Optional[float] = None
    budget: Optional[int] = None
    runtime: Optional[int] = None
    backdrop_path: Optional[str] = None
    revenue: Optional[int] = None
    overview: Optional[str] = None
    tagline: Optional[str] = None

    @field_validator('media_type', mode='before')
    def validate_media_type(cls, value):
        if value == "person":
            return None
        else:
            return value


class SeasonSchema(BaseModel):
    season_number: int
    name: str
    episode_count: int
    watched_episodes: Optional[int] = None
    watched: Optional[bool] = None


class EpisodeSchema(BaseModel):
    episode_number: int


class TVSchema(BaseModel):
    id: int
    media_type: Optional[str] = None
    name: Optional[str] = None
    first_air_date: Optional[str] = None
    last_air_date: Optional[str] = None
    poster_path: Optional[str] = None
    overview: Optional[str] = None
    vote_average: Optional[float] = None
    seasons: Optional[list[SeasonSchema]] = None
    number_of_episodes: Optional[int] = None
    buttons: Optional[str] = None
    popularity: Optional[float] = None
    backdrop_path: Optional[str] = None
    tagline: Optional[str] = None

    @field_validator('media_type', mode='before')
    def validate_media_type(cls, value):
        if value == "person":
            return None
        else:
            return value


class SearchContentSchema(BaseModel):
    page: int
    results: Optional[list[MovieSchema | TVSchema]] = None
    total_pages: int
    total_results: int


class  ButtonsId(BaseModel):
    buttons_id: str


class Genre(BaseModel):
    id: int
    name: str


class TvDetailsSchema(BaseModel):
    adult: bool
    backdrop_path: Optional[str] = None
    created_by: list[dict]
    first_air_date: Optional[str] = None
    genres: Optional[list[Genre]] = None
    homepage: Optional[str] = None
    id: int
    in_production: bool
    last_air_date: Optional[str] = None
    last_episode_to_air: dict
    name: str
    number_of_episodes: Optional[int] = None
    number_of_seasons: int
    original_name: Optional[str] = None
    overview: Optional[str] = None
    popularity: Optional[float] = None
    poster_path: Optional[str] = None
    seasons: Optional[list[SeasonSchema]] = None
    status: Optional[str] = None
    tagline: Optional[str] = None
    type: Optional[str] = None
    vote_average: Optional[float] = None
    watched: Optional[bool] = None
    watched_percent: Optional[int | float] = None
    media_type: Optional[str] = "tv"


class CrewPersonSchema(BaseModel):
    adult: bool
    gender: int
    id: int
    known_for_department: Optional[str] = None
    name: Optional[str] = None
    original_name: Optional[str] = None
    popularity: Optional[float] = None
    profile_path: Optional[str] = None
    credit_id: str
    department: Optional[str] = None
    job: Optional[str] = None


class CastPersonSchema(BaseModel):
    adult: bool
    gender: int
    id: int
    known_for_department: Optional[str] = None
    name: Optional[str] = None
    original_name: Optional[str] = None
    popularity: Optional[float] = None
    profile_path: Optional[str] = None
    credit_id: str
    character: Optional[str] = None
    order: int


class ContentCreditsSchema(BaseModel):
    cast: Optional[list[CastPersonSchema]] = None
    crew: Optional[list[CrewPersonSchema]] = None
    id: int


class TvRecommendSchema(BaseModel):
    page: int
    results: Optional[list[TVSchema]] = None
    total_pages: int
    total_results: int


class TvPageSchema(BaseModel):
    details: TvDetailsSchema
    credits: ContentCreditsSchema
    recommendations: TvRecommendSchema


class MovieDetailsSchema(BaseModel):
    adult: bool
    backdrop_path: Optional[str] = None
    budget: Optional[int] = None
    genres:  Optional[list[Genre]] = None
    id: int
    origin_country: Optional[list[str]] = None
    original_title: Optional[str]
    overview: Optional[str] = None
    popularity: Optional[float] = None
    poster_path: Optional[str] = None
    release_date: Optional[str] = None
    revenue: Optional[int] = None
    runtime: Optional[int] = None
    status: str
    tagline: Optional[str] = None
    title: Optional[str] = None
    vote_average: Optional[float] = None


class MovieRecommendSchema(BaseModel):
    page: int
    results: Optional[list[MovieSchema]] = None
    total_pages: int
    total_results: int


class MoviePageSchema(BaseModel):
    details: MovieDetailsSchema
    credits: ContentCreditsSchema
    recommendations: MovieRecommendSchema


class PopularMovies(BaseModel):
    page: int
    results: Optional[list[MovieSchema]] = None
    total_pages: int
    total_results: int


class UpcomingMovies(BaseModel):
    dates: dict
    page: int
    results: Optional[list[MovieSchema]] = None
    total_pages: int
    total_results: int


class PopularTvs(BaseModel):
    page: int
    results: Optional[list[TVSchema]] = None
    total_pages: int
    total_results: int


class AiringTodayTv(BaseModel):
    page: int
    results: Optional[list[TVSchema]] = None
    total_pages: int
    total_results: int


class IndexSchema(BaseModel):
    popular_movies: PopularMovies
    upcoming_movies: UpcomingMovies
    popular_tv: PopularTvs
    airing_today_tv: AiringTodayTv
