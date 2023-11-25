import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator

from .task import Task


class Column(BaseModel):
    id: uuid.UUID
    title: str
    child_id: uuid.UUID | None
    tasks: list[Task] | None

    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class ColumnCreate(BaseModel):
    title: str

    @field_validator('title')
    def title_must_be_valid(cls, value):
        if not value:
            raise ValueError("Заголовок не может быть пустым")

        if len(value) > 64:
            raise ValueError("Заголовок не может содержать больше 64 символов")
        return value


class ColumnUpdate(BaseModel):
    title: str = None
    child_id: uuid.UUID | None = None

    class Config:
        extra = 'ignore'

    @field_validator('title')
    def title_must_be_valid(cls, value):
        if value and len(value) > 64:
            raise ValueError("Название не может содержать больше 64 символов")
        return value
