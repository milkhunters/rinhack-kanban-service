import uuid

from pydantic import BaseModel, field_validator
from datetime import datetime


class Task(BaseModel):
    id: uuid.UUID
    title: str
    color: str
    content: str | None
    story_point: int
    start_time: datetime | None
    end_time: datetime | None
    executor_id: uuid.UUID | None
    column_id: uuid.UUID
    child_id: uuid.UUID | None

    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    title: str
    color: str = "#8DA2DB"
    story_point: int = 0
    start_time: datetime | None = None
    end_time: datetime | None = None
    executor_id: uuid.UUID | None = None
    column_id: uuid.UUID | None = None
    content: str

    class Config:
        extra = 'ignore'

    @field_validator('title')
    def title_must_be_valid(cls, value):
        if not value:
            raise ValueError("Заголовок не может быть пустым")

        if len(value) > 64:
            raise ValueError("Заголовок не может содержать больше 64 символов")
        return value

    @field_validator('story_point')
    def story_must_be_valid(cls, value: str):
        if not value:
            raise ValueError("SP не может быть пустым")

        try:
            int(value)
        except ValueError:
            raise ValueError("SP не является числом")

        if not (0 <= int(value) <= 5000):
            raise ValueError("SP должен быть в диапазоне от 0 до 5000")

        return value

    @field_validator('color')
    def color_must_be_valid(cls, value: str):
        if not value:
            raise ValueError("Значение цвета не может быть пустым!")

        if len(value) != 7 or not value.startswith("#"):
            raise ValueError("Значение цвета некорректно!")
        return value

    @field_validator('content')
    def content_must_be_valid(cls, value):
        if not value:
            return

        if len(value) > 10000:
            raise ValueError("Содержание не может быть больше 10000 символов")
        return value


class TaskUpdate(BaseModel):
    title: str = None
    color: str = None
    content: str = None
    story_point: int = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    executor_id: uuid.UUID | None = None
    column_id: uuid.UUID = None
    child_id: uuid.UUID | None = None

    class Config:
        extra = 'ignore'

    @field_validator('title')
    def title_must_be_valid(cls, value):
        if not value:
            return

        if len(value) > 64:
            raise ValueError("Заголовок не может содержать больше 64 символов")
        return value

    @field_validator('story_point')
    def story_must_be_valid(cls, value: str):
        if not value:
            raise

        if not (0 <= int(value) <= 5000):
            raise ValueError("SP должен быть в диапазоне от 0 до 5000")

        return value

    @field_validator('color')
    def color_must_be_valid(cls, value: str):
        if not value:
            return

        if len(value) != 7 or not value.startswith("#"):
            raise ValueError("Значение цвета некорректно!")
        return value

    @field_validator('content')
    def content_must_be_valid(cls, value):
        if not value:
            return

        if len(value) > 10000:
            raise ValueError("Содержание не может быть больше 10000 символов")
        return value
