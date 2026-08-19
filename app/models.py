from datetime import datetime
from enum import StrEnum
from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase): pass

class JobState(StrEnum):
    PENDING="PENDING"; PROCESSING="PROCESSING"; READY="READY"; UPLOADING="UPLOADING"; COMPLETED="COMPLETED"; FAILED="FAILED"; CANCELLED="CANCELLED"

class User(Base):
    __tablename__="users"
    id: Mapped[int]=mapped_column(primary_key=True)
    telegram_id: Mapped[int]=mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str|None]=mapped_column(String(255))
    name: Mapped[str|None]=mapped_column(String(255))
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now())
    uploads: Mapped[list["Upload"]]=relationship(back_populates="user")

class Channel(Base):
    __tablename__="channels"
    id: Mapped[int]=mapped_column(primary_key=True)
    telegram_chat_id: Mapped[int]=mapped_column(BigInteger, unique=True, index=True)
    title: Mapped[str]=mapped_column(String(255))
    enabled: Mapped[bool]=mapped_column(Boolean, default=True)
    thumbnail_path: Mapped[str|None]=mapped_column(Text)
    caption_template: Mapped[str|None]=mapped_column(Text)
    button_template: Mapped[dict|None]=mapped_column(JSON)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now())

class File(Base):
    __tablename__="files"
    id: Mapped[int]=mapped_column(primary_key=True)
    path: Mapped[str]=mapped_column(Text)
    original_name: Mapped[str]=mapped_column(Text)
    size: Mapped[int]=mapped_column(BigInteger)
    sha256: Mapped[str]=mapped_column(String(64), index=True)
    mime_type: Mapped[str|None]=mapped_column(String(255))
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now())

class Media(Base):
    __tablename__="media"
    id: Mapped[int]=mapped_column(primary_key=True)
    file_id: Mapped[int]=mapped_column(ForeignKey("files.id"), unique=True)
    title: Mapped[str|None]=mapped_column(String(500))
    original_title: Mapped[str|None]=mapped_column(String(500))
    year: Mapped[int|None]=mapped_column(Integer)
    poster: Mapped[str|None]=mapped_column(Text)
    backdrop: Mapped[str|None]=mapped_column(Text)
    genres: Mapped[list|None]=mapped_column(JSON)
    rating: Mapped[float|None]=mapped_column()
    overview: Mapped[str|None]=mapped_column(Text)
    season: Mapped[int|None]=mapped_column(Integer)
    episode: Mapped[int|None]=mapped_column(Integer)
    trailer_url: Mapped[str|None]=mapped_column(Text)

class Anime(Base):
    __tablename__="anime"
    id: Mapped[int]=mapped_column(primary_key=True)
    title: Mapped[str]=mapped_column(String(500), unique=True)
    metadata_json: Mapped[dict|None]=mapped_column(JSON)

class Episode(Base):
    __tablename__="episodes"
    id: Mapped[int]=mapped_column(primary_key=True)
    anime_id: Mapped[int]=mapped_column(ForeignKey("anime.id"), index=True)
    season: Mapped[int|None]=mapped_column(Integer)
    episode: Mapped[int|None]=mapped_column(Integer)
    metadata_json: Mapped[dict|None]=mapped_column(JSON)
    __table_args__=(UniqueConstraint("anime_id","season","episode"),)

class Upload(Base):
    __tablename__="uploads"
    id: Mapped[int]=mapped_column(primary_key=True)
    user_id: Mapped[int]=mapped_column(ForeignKey("users.id"), index=True)
    file_id: Mapped[int]=mapped_column(ForeignKey("files.id"), index=True)
    channel_id: Mapped[int]=mapped_column(ForeignKey("channels.id"), index=True)
    state: Mapped[str]=mapped_column(String(20), default=JobState.PENDING, index=True)
    priority: Mapped[int]=mapped_column(Integer, default=0, index=True)
    idempotency_key: Mapped[str]=mapped_column(String(128), unique=True, index=True)
    caption: Mapped[str|None]=mapped_column(Text)
    message_id: Mapped[int|None]=mapped_column(BigInteger)
    retries: Mapped[int]=mapped_column(Integer, default=0)
    error: Mapped[str|None]=mapped_column(Text)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    user: Mapped[User]=relationship(back_populates="uploads")

class QueueJob(Base):
    __tablename__="queue_jobs"
    id: Mapped[int]=mapped_column(primary_key=True)
    upload_id: Mapped[int]=mapped_column(ForeignKey("uploads.id"), unique=True)
    state: Mapped[str]=mapped_column(String(20), default=JobState.PENDING, index=True)
    available_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    attempts: Mapped[int]=mapped_column(Integer, default=0)
    last_error: Mapped[str|None]=mapped_column(Text)

class ScheduledJob(Base):
    __tablename__="scheduled_jobs"
    id: Mapped[int]=mapped_column(primary_key=True)
    upload_id: Mapped[int]=mapped_column(ForeignKey("uploads.id"), index=True)
    run_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), index=True)
    cron: Mapped[str|None]=mapped_column(String(255))
    timezone: Mapped[str]=mapped_column(String(100))
    enabled: Mapped[bool]=mapped_column(Boolean, default=True)

class Thumbnail(Base):
    __tablename__="thumbnails"
    id: Mapped[int]=mapped_column(primary_key=True)
    media_id: Mapped[int]=mapped_column(ForeignKey("media.id"), index=True)
    path: Mapped[str]=mapped_column(Text)
    timestamp: Mapped[float]=mapped_column(default=0)
    sha256: Mapped[str]=mapped_column(String(64), index=True)

class RenameRule(Base):
    __tablename__="rename_rules"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(255), unique=True)
    regex: Mapped[str]=mapped_column(Text)
    template: Mapped[str]=mapped_column(Text)
    enabled: Mapped[bool]=mapped_column(Boolean, default=True)

class Plan(Base):
    __tablename__="plans"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(100), unique=True)
    limits: Mapped[dict]=mapped_column(JSON)
    features: Mapped[list]=mapped_column(JSON)

class Subscription(Base):
    __tablename__="subscriptions"
    id: Mapped[int]=mapped_column(primary_key=True)
    user_id: Mapped[int]=mapped_column(ForeignKey("users.id"), index=True)
    plan_id: Mapped[int]=mapped_column(ForeignKey("plans.id"))
    started_at: Mapped[datetime]=mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[str]=mapped_column(String(30), index=True)

class Setting(Base):
    __tablename__="settings"
    key: Mapped[str]=mapped_column(String(255), primary_key=True)
    value: Mapped[dict]=mapped_column(JSON)

class AuditLog(Base):
    __tablename__="audit_logs"
    id: Mapped[int]=mapped_column(primary_key=True)
    actor_telegram_id: Mapped[int]=mapped_column(BigInteger, index=True)
    action: Mapped[str]=mapped_column(String(255), index=True)
    payload: Mapped[dict|None]=mapped_column(JSON)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now())
