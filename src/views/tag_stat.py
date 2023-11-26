from .base import BaseView
from src.models import schemas


class TagStatResponse(BaseView):
    content: [schemas.TagStat]
