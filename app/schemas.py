from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr


# ---------------------------------------------------------------------------
# User schemas
# ---------------------------------------------------------------------------


class UserCreate(BaseModel):
    email: str
    name: str
    interests: list[str] = []


class UserUpdate(BaseModel):
    interests: list[str]


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    interests: list[str]
    created_at: datetime


# ---------------------------------------------------------------------------
# Snippet schemas
# ---------------------------------------------------------------------------


class SnippetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: str
    title: str
    source: str
    article_url: str
    script: str
    word_count: int
    audio_file: str | None
    created_at: datetime


# ---------------------------------------------------------------------------
# Interaction schemas
# ---------------------------------------------------------------------------


class InteractionCreate(BaseModel):
    snippet_id: int
    action: Literal["played", "completed", "skipped"]


# ---------------------------------------------------------------------------
# Feed schemas
# ---------------------------------------------------------------------------


class FeedResponse(BaseModel):
    snippets: list[SnippetResponse]
    total: int


# ---------------------------------------------------------------------------
# Admin / generation status schemas
# ---------------------------------------------------------------------------


class GenerationStatus(BaseModel):
    status: str
    snippets_generated: int
    errors: int
    started_at: str | None
    completed_at: str | None
