import os
from typing import Callable, Coroutine, Any
from uuid import UUID

from src import exceptions
from src.config import Config
from src.models import schemas
from src.models.permission import Permission
from src.models.state import UserState
from src.services.auth import state_filter, permission_filter
from src.services.repository import TagRepo, TaskRepo


class StatsApplicationService:

    def __init__(
            self,
            current_user,
            config: Config,
            tag_repo: TagRepo,
            task_repo: TaskRepo,
            is_user_in_project: Callable[[UUID, UUID], Coroutine[Any, Any, bool]],
    ):
        self._current_user = current_user
        self._config = config
        self._tag_repo = tag_repo
        self._task_repo = task_repo
        self._is_user_in_project = is_user_in_project

    async def get_stats(self, details: bool = False) -> dict:
        info = {
            "version": self._config.BASE.VERSION,
        }
        if details:
            info.update(
                {
                    "DEBUG": self._config.DEBUG,
                    "build": os.getenv("BUILD", "unknown"),
                    "branch": os.getenv("BRANCH", "unknown"),
                }
            )
        return info

    @state_filter(UserState.ACTIVE)
    @permission_filter(Permission.GET_TASK)
    async def get_tag_stat(self, project_id: UUID) -> list[schemas.TagStat]:
        if not await self._is_user_in_project(project_id, self._current_user.id):
            raise exceptions.AccessDenied("Доступ запрещен")

        result = []

        tags = await self._tag_repo.get_all(project_id=project_id)
        if not tags:
            return result

        for tag in tags:
            result.append(
                schemas.TagStat(
                    title=tag.title,
                    count=await self._tag_repo.get_task_count(tag.id)
                )
            )
        return result

    @state_filter(UserState.ACTIVE)
    @permission_filter(Permission.GET_TASK)
    async def get_task_stat(self, project_id: UUID) -> list[schemas.TaskCountStat]:
        if not await self._is_user_in_project(project_id, self._current_user.id):
            raise exceptions.AccessDenied("Доступ запрещен")

        result = []

        all_task_count = await self._task_repo.all_count(project_id=project_id)
        result.append(
            schemas.TaskCountStat(
                status="all",
                count=0 if not all_task_count else all_task_count
            )
        )

        active_task_count = await self._task_repo.active_count(project_id=project_id)
        result.append(
            schemas.TaskCountStat(
                status="active",
                count=0 if not active_task_count else active_task_count
            )
        )

        done_task_count = await self._task_repo.done_count(project_id=project_id)
        result.append(
            schemas.TaskCountStat(
                status="done",
                count=0 if not done_task_count else done_task_count
            )
        )
        return result



