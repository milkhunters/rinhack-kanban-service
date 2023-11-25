import uuid
from typing import Callable, Coroutine, Any

from src import exceptions
from src.models import schemas
from src.models.permission import Permission
from src.models.auth import BaseUser
from src.models.state import UserState
from src.services.auth.filters import state_filter
from src.services.auth.filters import permission_filter
from src.services.repository import ColumnRepo
from src.services.repository import TaskRepo


class KanbanApplicationService:

    def __init__(
            self,
            current_user: BaseUser,
            column_repo: ColumnRepo,
            task_repo: TaskRepo,
            is_user_in_project: Callable[[uuid.UUID, uuid.UUID], Coroutine[Any, Any, bool]],
    ):
        self._current_user = current_user
        self._repo = column_repo
        self._task_repo = task_repo
        self._is_user_in_project = is_user_in_project

    @state_filter(UserState.ACTIVE)
    @permission_filter(Permission.GET_COLUMN)
    async def column_list(self, project_id: uuid.UUID) -> list[schemas.Column]:
        if not await self._is_user_in_project(project_id, self._current_user.id):
            raise exceptions.AccessDenied("Доступ запрещен")

        columns = await self._repo.get_all(project_id=project_id)
        return [schemas.Column.model_validate(column) for column in columns]

    @state_filter(UserState.ACTIVE)
    @permission_filter(Permission.GET_COLUMN)
    async def get_column(self, column_id: uuid.UUID) -> schemas.Column:
        column = await self._repo.get(id=column_id)
        if not column:
            raise exceptions.NotFound("Колонка не найдена")

        if not await self._is_user_in_project(column.project_id, self._current_user.id):
            raise exceptions.AccessDenied("Доступ запрещен")

        return schemas.Column.model_validate(column)

    @state_filter(UserState.ACTIVE)
    @permission_filter(Permission.CREATE_COLUMN)
    async def create_column(self, project_id: uuid.UUID, data: schemas.ColumnCreate) -> schemas.Column:

        if not await self._is_user_in_project(project_id, self._current_user.id):
            raise exceptions.AccessDenied("Доступ запрещен")

        last_column = await self._repo.get(child_id=None, project_id=project_id)
        column = await self._repo.create(**data.model_dump(), project_id=project_id)

        if last_column:
            await self._repo.update(last_column.id, child_id=column.id)

        # Task preloading
        column = await self._repo.get(id=column.id)
        return schemas.Column.model_validate(column)

    @state_filter(UserState.ACTIVE)
    @permission_filter(Permission.UPDATE_COLUMN)
    async def update_column(self, column_id: uuid.UUID, data: schemas.ColumnUpdate) -> None:
        column = await self._repo.get(id=column_id)
        if not column:
            raise exceptions.NotFound("Колонка не найдена")

        if not await self._is_user_in_project(column.project_id, self._current_user.id):
            raise exceptions.AccessDenied("Доступ запрещен")

        # Обновить порядок колонок
        if column.child_id != data.child_id:

            # Дочерняя колонка может быть либо None, либо валидным Column
            new_child_id = data.child_id
            if new_child_id:
                child_column = await self._repo.get(id=new_child_id)
                if not child_column:
                    raise exceptions.NotFound("Дочерняя колонка не найдена")

                if child_column.project_id != column.project_id:
                    raise exceptions.BadRequest("Дочерняя колонка не принадлежит данному проекту")

            parent_column = await self._repo.get(child_id=column_id)
            if parent_column:
                await self._repo.update(parent_column.id, child_id=column.child_id)

            # Может быть null
            if new_child_id:
                new_parent_column = await self._repo.get(child_id=new_child_id)
            else:
                new_parent_column = await self._repo.get(child_id=None)

            if new_parent_column:
                await self._repo.update(new_parent_column.id, child_id=column_id)

        await self._repo.update(column_id, **data.model_dump())

    @state_filter(UserState.ACTIVE)
    @permission_filter(Permission.DELETE_COLUMN)
    async def delete_column(self, column_id: uuid.UUID) -> None:
        column = await self._repo.get(id=column_id)
        if not column:
            raise exceptions.NotFound("Колонка не найдена")

        if not await self._is_user_in_project(column.project_id, self._current_user.id):
            raise exceptions.AccessDenied("Доступ запрещен")

        pre_column = await self._repo.get(child_id=column_id)

        if pre_column:
            await self._repo.update(pre_column.id, child_id=column.child_id)

        await self._repo.delete(id=column_id)

    @state_filter(UserState.ACTIVE)
    @permission_filter(Permission.GET_TASK)
    async def task_list(self, column_id: uuid.UUID) -> list[schemas.Task]:
        column = await self._repo.get(id=column_id)
        if not column:
            raise exceptions.NotFound("Колонка не найдена")

        if not await self._is_user_in_project(column.project_id, self._current_user.id):
            raise exceptions.AccessDenied("Доступ запрещен")

        # Todo: сортировка
        tasks = await self._task_repo.get_all(column_id=column_id)
        return [schemas.Task.model_validate(task) for task in tasks]

    @state_filter(UserState.ACTIVE)
    @permission_filter(Permission.GET_TASK)
    async def get_task(self, task_id: uuid.UUID) -> schemas.Task:
        task = await self._task_repo.get(id=task_id)
        if not task:
            raise exceptions.NotFound("Задача не найдена")

        if not await self._is_user_in_project(task.column.project_id, self._current_user.id):
            raise exceptions.AccessDenied("Доступ запрещен")

        return schemas.Task.model_validate(task)

    @state_filter(UserState.ACTIVE)
    @permission_filter(Permission.CREATE_TASK)
    async def create_task(self, column_id: uuid.UUID, data: schemas.TaskCreate) -> schemas.Task:
        column = await self._repo.get(id=column_id)
        if not column:
            raise exceptions.NotFound("Колонка не найдена")

        if not await self._is_user_in_project(column.project_id, self._current_user.id):
            raise exceptions.AccessDenied("Доступ запрещен")

        last_task = await self._task_repo.get(child_id=None, column_id=column_id)
        task = await self._task_repo.create(**data.model_dump(), column_id=column_id)

        if last_task:
            await self._task_repo.update(last_task.id, child_id=task.id)

        return schemas.Task.model_validate(task)

    @state_filter(UserState.ACTIVE)
    @permission_filter(Permission.UPDATE_TASK)
    async def update_task(self, task_id: uuid.UUID, data: schemas.TaskUpdate) -> None:
        task = await self._repo.get(id=task_id)
        if not task:
            raise exceptions.NotFound("Задача не найдена")

        if not await self._is_user_in_project(task.column.project_id, self._current_user.id):
            raise exceptions.AccessDenied("Доступ запрещен")

        #  TODO: Обновить порядок колонок

        await self._task_repo.update(task_id, **data.model_dump(exclude_unset=True))

    @state_filter(UserState.ACTIVE)
    @permission_filter(Permission.DELETE_TASK)
    async def delete_task(self, task_id: uuid.UUID) -> None:
        task = await self._task_repo.get(id=task_id)
        if not task:
            raise exceptions.NotFound("Задача не найдена")

        if not await self._is_user_in_project(task.column.project_id, self._current_user.id):
            raise exceptions.AccessDenied("Доступ запрещен")

        pre_task = await self._task_repo.get(child_id=task_id)

        if pre_task:
            await self._task_repo.update(pre_task.id, child_id=task.child_id)

        await self._task_repo.delete(id=task_id)

