import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator


class Tag(BaseModel):
    id: uuid.UUID
    title: str

    created_at: datetime

    class Config:
        from_attributes = True


class TagCreate(BaseModel):
    title: str

    class Config:
        extra = 'ignore'

    @field_validator('title')
    def title_must_be_valid(cls, value):
        if not value:
            raise ValueError("Тег не может быть пустым")

        if len(value) > 32:
            raise ValueError("Тег не может содержать больше 32 символов")
        return value


class TagStat(BaseModel):
    title: str
    count: int
