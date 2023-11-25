from .base import BaseView
from src.models import schemas


class TaskResponse(BaseView):
    content: schemas.Task


class TasksResponse(BaseView):
    content: list[schemas.Task]
