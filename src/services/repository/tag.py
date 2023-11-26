import uuid

from src.models import tables
from src.services.repository.base import BaseRepository


class TagRepo(BaseRepository[tables.Tag]):
    table = tables.Tag

    async def get_task_count(self, tag_id: uuid.UUID) -> int:
        stmt = (
            self.table.select()
            .join(tables.TaskTag)
            .where(tables.TaskTag.tag_id == tag_id)
            .count()
        )
        result = await self.session.execute(stmt)
        return result.scalar()
