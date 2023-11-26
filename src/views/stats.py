from .base import BaseView
from src.models import schemas


class TagStatResponse(BaseView):
    content: list[schemas.TagStat]


class TaskCountStatResponse(BaseView):
    content: list[schemas.TaskCountStat]
