from sqlalchemy import select
from sqlalchemy.orm import subqueryload

from src.models import tables
from .base import BaseRepository


class TaskRepo(BaseRepository[tables.Task]):
    table = tables.Task

    async def get(self, **kwargs) -> tables.Task:
        stmt = select(self.table).filter_by(**kwargs).options(subqueryload(self.table.column))
        return (await self._session.execute(stmt)).scalars().first()
