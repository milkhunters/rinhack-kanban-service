import uuid

from sqlalchemy import select, insert, delete
from sqlalchemy.orm import subqueryload

from src.models import tables
from .base import BaseRepository


class TaskRepo(BaseRepository[tables.Task]):
    table = tables.Task

    async def get(self, **kwargs) -> tables.Task:
        stmt = select(
            self.table
        ).filter_by(**kwargs).options(subqueryload(self.table.column)).options(subqueryload(self.table.tags))
        return (await self._session.execute(stmt)).scalars().first()

    async def add_tag(self, task_id: uuid.UUID, tag_id: uuid.UUID) -> None:
        stmt = insert(tables.TaskTag).values(task_id=task_id, tag_id=tag_id)
        await self._session.execute(stmt)
        await self._session.commit()

    async def remove_tag(self, task_id: uuid.UUID, tag_id: uuid.UUID) -> None:
        stmt = delete(tables.TaskTag).where(tables.TaskTag.task_id == task_id).where(tables.TaskTag.tag_id == tag_id)
        await self._session.execute(stmt)
        await self._session.commit()

    async def has_tag(self, task_id: uuid.UUID, tag_id: uuid.UUID) -> bool:
        stmt = select(tables.TaskTag).where(tables.TaskTag.task_id == task_id).where(tables.TaskTag.tag_id == tag_id)
        return (await self._session.execute(stmt)).scalars().first() is not None

    async def create(self, **kwargs) -> tables.Task:
        model = self.table(**kwargs)
        self._session.add(model)
        await self._session.commit()
        return (await self.session.execute(select(self.table).filter_by(id=model.id).options(
            subqueryload(self.table.tags)
        ))).scalars().first()
