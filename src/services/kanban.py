import uuid
from typing import Callable, Coroutine, Any

from src import exceptions
from src.models import schemas
from src.models.auth import BaseUser
from src.models.permission import Permission
from src.models.state import UserState
from src.services.auth.filters import permission_filter
from src.services.auth.filters import state_filter
from src.services.repository import ColumnRepo, TagRepo
from src.services.repository import TaskRepo


class KanbanApplicationService:

    def __init__(
            self,
            current_user: BaseUser,
            column_repo: ColumnRepo,
            task_repo: TaskRepo,
            tag_repo: TagRepo,
            is_user_in_project: Callable[[uuid.UUID, uuid.UUID], Coroutine[Any, Any, bool]],
    ):
        self._current_user = current_user
        self._repo = column_repo
        self._task_repo = task_repo
        self._tag_repo = tag_repo
        self._is_user_in_project = is_user_in_project

    @state_filter(UserState.ACTIVE)
    @permission_filter(Permission.GET_COLUMN)
    async def column_list(self, project_id: uuid.UUID) -> list[schemas.Column]:
        if not await self._is_user_in_project(project_id, self._current_user.id):
            raise exceptions.AccessDenied("Доступ запрещен")

        _ = await self._repo.get_all(project_id=project_id)
        columns = [schemas.Column.model_validate(column) for column in _]
        # Сортировка задач колонок
        for column in columns:
            task_ids = {el.id for el in column.tasks}
            task_child_ids = {el.child_id for el in column.tasks}
            result = list(task_ids - task_child_ids)

            if not result:
                continue

            sorted_tasks = []
            current_task = [el for el in column.tasks if el.id == result[0]][0]
            while True:
                sorted_tasks.append(current_task)
                searched = [el for el in column.tasks if el.id == current_task.child_id]
                if searched:
                    current_task = searched[0]
                    continue
                break
            column.tasks = sorted_tasks

        # Сортировка колонок
        column_ids = {el.id for el in columns}
        column_child_ids = {el.child_id for el in columns}
        result = list(column_ids - column_child_ids)

        if result:
            sorted_columns = []
            current_column = [el for el in columns if el.id == result[0]][0]
            while True:
                sorted_columns.append(current_column)
                searched = [el for el in columns if el.id == current_column.child_id]
                if searched:
                    current_column = searched[0]
                    continue
                break
            columns = sorted_columns
        return columns

    @state_filter(UserState.ACTIVE)
    @permission_filter(Permission.GET_COLUMN)
    async def get_column(self, column_id: uuid.UUID) -> schemas.Column:
        column = await self._repo.get(id=column_id)
        if not column:
            raise exceptions.NotFound("Колонка не найдена")

        if not await self._is_user_in_project(column.project_id, self._current_user.id):
            raise exceptions.AccessDenied("Доступ запрещен")

        # Сортировка
        task_ids = {el.id for el in column.tasks}
        task_child_ids = {el.child_id for el in column.tasks}
        result = list(task_ids - task_child_ids)

        if result:
            sorted_tasks = []
            current_task = [el for el in column.tasks if el.id == result[0]][0]
            while True:
                sorted_tasks.append(current_task)
                searched = [el for el in column.tasks if el.id == current_task.child_id]
                if searched:
                    current_task = searched[0]
                    continue
                break
            column.tasks = sorted_tasks

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

        column = schemas.Column.model_validate(column)

        # Сортировка
        task_ids = {el.id for el in column.tasks}
        task_child_ids = {el.child_id for el in column.tasks}
        result = list(task_ids - task_child_ids)

        if result:
            sorted_tasks = []
            current_task = [el for el in column.tasks if el.id == result[0]][0]
            while True:
                sorted_tasks.append(current_task)
                searched = [el for el in column.tasks if el.id == current_task.child_id]
                if searched:
                    current_task = searched[0]
                    continue
                break
            column.tasks = sorted_tasks
        return column.tasks

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
        task = await self._task_repo.get(id=task_id)
        if not task:
            raise exceptions.NotFound("Задача не найдена")

        if not await self._is_user_in_project(task.column.project_id, self._current_user.id):
            raise exceptions.AccessDenied("Доступ запрещен")

        if data.column_id:
            new_column = await self._repo.get(id=data.column_id)
            if not new_column:
                raise exceptions.NotFound("Новая колонка не найдена")

            if not await self._is_user_in_project(new_column.project_id, self._current_user.id):
                raise exceptions.AccessDenied("Доступ к указанной колонке запрещен")

        # Обновить порядок задач
        if (not data.column_id or task.column_id == data.column_id) and task.child_id != data.child_id:

            # Дочерняя колонка может быть либо None, либо валидным Column
            new_child_id = data.child_id
            if new_child_id:
                child_task = await self._task_repo.get(id=new_child_id)
                if not child_task:
                    raise exceptions.NotFound("Дочерняя карточка не найдена")

                if child_task.column.project_id != task.column.project_id:
                    raise exceptions.BadRequest("Дочерняя карточка не принадлежит данному проекту")

            parent_task = await self._task_repo.get(child_id=task_id)
            if parent_task:
                await self._task_repo.update(parent_task.id, child_id=task.child_id)

            # Может быть null
            if new_child_id:
                new_parent_task = await self._task_repo.get(child_id=new_child_id)
            else:
                new_parent_task = await self._task_repo.get(child_id=None)

            if new_parent_task:
                await self._task_repo.update(new_parent_task.id, child_id=task_id)

        elif data.column_id and task.column_id != data.column_id:
            # Удаление задачи из колонки
            pre_task = await self._task_repo.get(child_id=task_id)
            if pre_task:
                await self._task_repo.update(pre_task.id, child_id=task.child_id)

            await self._task_repo.delete(id=task_id)

            # Создание задачи в новой колонке
            last_task = await self._task_repo.get(child_id=None, column_id=data.column_id)
            task = await self._task_repo.create(
                **schemas.Task.model_validate(task).model_dump(
                    exclude={"column_id", "child_id"}
                ),
                column_id=data.column_id,
                child_id=None
            )

            if last_task:
                await self._task_repo.update(last_task.id, child_id=task.id)

            # Перемещение в новой колонке
            new_child_id = data.child_id
            if new_child_id:
                child_task = await self._task_repo.get(id=new_child_id)
                if not child_task:
                    raise exceptions.NotFound("Дочерняя карточка не найдена")

                if child_task.column.project_id != task.column.project_id:
                    raise exceptions.BadRequest("Дочерняя карточка не принадлежит данному проекту")

            parent_task = await self._task_repo.get(child_id=task_id)
            if parent_task:
                await self._task_repo.update(parent_task.id, child_id=task.child_id)

            # Может быть null
            if new_child_id:
                new_parent_task = await self._task_repo.get(child_id=new_child_id)
            else:
                new_parent_task = await self._task_repo.get(child_id=None)

            if new_parent_task:
                await self._task_repo.update(new_parent_task.id, child_id=task_id)

        return await self._task_repo.update(task_id, **data.model_dump(exclude_unset=True))

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

    @state_filter(UserState.ACTIVE)
    @permission_filter(Permission.UPDATE_TASK)
    async def create_tag(self, project_id: uuid.UUID, data: schemas.TagCreate) -> schemas.Tag:
        if not await self._is_user_in_project(project_id, self._current_user.id):
            raise exceptions.AccessDenied("Доступ запрещен")

        _ = await self._tag_repo.get(title=data.title, project_id=project_id)
        if _:
            raise exceptions.BadRequest(f"Тег с названием {data.title!r} уже существует")

        tag = await self._tag_repo.create(**data.model_dump(), project_id=project_id)
        return schemas.Tag.model_validate(tag)

    @state_filter(UserState.ACTIVE)
    @permission_filter(Permission.UPDATE_TASK)
    async def delete_tag(self, tag_id: uuid.UUID) -> None:
        tag = await self._tag_repo.get(id=tag_id)
        if not tag:
            raise exceptions.NotFound("Тег не найден")

        if not await self._is_user_in_project(tag.project_id, self._current_user.id):
            raise exceptions.AccessDenied("Доступ запрещен")

        await self._tag_repo.delete(tag.id)

    @state_filter(UserState.ACTIVE)
    @permission_filter(Permission.GET_TASK)
    async def tag_list(self, project_id: uuid.UUID) -> list[schemas.Tag]:
        if not await self._is_user_in_project(project_id, self._current_user.id):
            raise exceptions.AccessDenied("Доступ запрещен")

        tags = await self._tag_repo.get_all(project_id=project_id)
        return [schemas.Tag.model_validate(tag) for tag in tags]

    @state_filter(UserState.ACTIVE)
    @permission_filter(Permission.UPDATE_TASK)
    async def set_tag(self, task_id: uuid.UUID, tag_id: uuid.UUID) -> None:
        task = await self._task_repo.get(id=task_id)
        if not task:
            raise exceptions.NotFound("Задача не найдена")

        if not await self._is_user_in_project(task.column.project_id, self._current_user.id):
            raise exceptions.AccessDenied("Доступ запрещен")

        tag = await self._tag_repo.get(id=tag_id)
        if not tag:
            raise exceptions.NotFound("Тег не найден")

        if await self._task_repo.has_tag(task_id=task_id, tag_id=tag_id):
            raise exceptions.NotFound("Связь уже существует")

        await self._task_repo.add_tag(task_id, tag_id)

    @state_filter(UserState.ACTIVE)
    @permission_filter(Permission.UPDATE_TASK)
    async def unset_tag(self, task_id: uuid.UUID, tag_id: uuid.UUID) -> None:
        task = await self._task_repo.get(id=task_id)
        if not task:
            raise exceptions.NotFound("Задача не найдена")

        if not await self._is_user_in_project(task.column.project_id, self._current_user.id):
            raise exceptions.AccessDenied("Доступ запрещен")

        tag = await self._tag_repo.get(id=tag_id)
        if not tag:
            raise exceptions.NotFound("Тег не найден")

        if not await self._task_repo.has_tag(task_id=task_id, tag_id=tag_id):
            raise exceptions.NotFound("Не найдена связь тега с карточкой")

        await self._task_repo.remove_tag(task_id, tag_id)
