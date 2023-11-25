from .base import BaseView
from src.models import schemas


class ColumnResponse(BaseView):
    content: schemas.Column


class ColumnsResponse(BaseView):
    content: list[schemas.Column]
