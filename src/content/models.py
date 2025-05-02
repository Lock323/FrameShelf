from enum import Enum
from database import Base
from sqlalchemy import UniqueConstraint, ForeignKey, event, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone


class MediaType(Enum):
    movie = "movie"
    tv = "tv"


class Status(Enum):
    watched = "watched"
    watchlist = "watchlist"


class ContentTable(Base):
    __tablename__ = "content"
    id: Mapped[int] = mapped_column(primary_key=True)
    tmdb_id: Mapped[int] = mapped_column(nullable=False)
    media_type: Mapped[MediaType] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=True)
    release_date: Mapped[str] = mapped_column(nullable=True)
    poster_path: Mapped[str] = mapped_column(nullable=True)
    vote_average: Mapped[float] = mapped_column(nullable=True)
    __table_args__ = (
        UniqueConstraint('tmdb_id', 'media_type', name='unique_tmdb_id_and_media_type'),
    )

class UserContentTable(Base):
    __tablename__ = "user_content"
    id: Mapped[int] = mapped_column(primary_key=True)
    users_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    content_id: Mapped[int] = mapped_column(ForeignKey("content.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[Status] = mapped_column()
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    __table_args__ = (
        UniqueConstraint('users_id', 'content_id', name='unique_user_id_and_content_id'),
    )


class SeasonEpisodeTable(Base):
    __tablename__ = "season_episode"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_content_id: Mapped[int] = mapped_column(ForeignKey("user_content.id", ondelete="CASCADE"),
                                                 nullable=False)
    season_number: Mapped[int] = mapped_column(nullable=False)
    season_name: Mapped[str]
    watched_episodes: Mapped[int]
    __table_args__ = (
        UniqueConstraint('user_content_id', 'season_number', name='unique_user_content_id_and_season_number'),
    )


def update_added_at(mapper, connection, target):
    target.added_at = datetime.now(tz=timezone.utc)


event.listen(UserContentTable, 'before_insert', update_added_at)
event.listen(UserContentTable, 'before_update', update_added_at)
