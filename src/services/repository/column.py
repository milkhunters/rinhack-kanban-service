from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import subqueryload, joinedload

from src.models import tables
from .base import BaseRepository
from ...models.tables import Column


class ColumnRepo(BaseRepository[tables.Column]):
    table = tables.Column

    async def get(self, **kwargs) -> tables.Column:
        stmt = select(
            self.table
        ).filter_by(**kwargs).options(
            joinedload(self.table.tasks).joinedload(tables.Task.tags)
        )
        return (await self._session.execute(stmt)).scalars().first()

    async def get_all(self, **kwargs) -> Sequence[Column]:
        stmt = select(
            self.table
        ).filter_by(**kwargs).options(
            joinedload(self.table.tasks).joinedload(tables.Task.tags)
        )
        return (await self._session.execute(stmt)).unique().scalars().all()
