from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    # Stored as a JSON array of category strings, e.g. ["tech", "nba"]
    interests: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    interactions: Mapped[list["UserSnippetInteraction"]] = relationship(
        "UserSnippetInteraction", back_populates="user"
    )


class Snippet(Base):
    __tablename__ = "snippets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    category: Mapped[str] = mapped_column(String, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)
    article_url: Mapped[str] = mapped_column(String, nullable=False)
    published_at: Mapped[str] = mapped_column(String, nullable=True)
    script: Mapped[str] = mapped_column(Text, nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, nullable=False)
    audio_file: Mapped[str | None] = mapped_column(String, nullable=True)
    has_whoosh: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False,
                                             server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    interactions: Mapped[list["UserSnippetInteraction"]] = relationship(
        "UserSnippetInteraction", back_populates="snippet"
    )


class UserSnippetInteraction(Base):
    __tablename__ = "user_snippet_interactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    snippet_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("snippets.id"), nullable=False
    )
    # "played", "completed", "skipped"
    action: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    user: Mapped["User"] = relationship("User", back_populates="interactions")
    snippet: Mapped["Snippet"] = relationship("Snippet", back_populates="interactions")
