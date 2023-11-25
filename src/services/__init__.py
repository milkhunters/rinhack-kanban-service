from src.models.auth import BaseUser
from . import auth
from . import repository
from .kanban import KanbanApplicationService
from .permission import PermissionApplicationService
from .project import is_user_in_project
from .stats import StatsApplicationService
from ..config import Config


class ServiceFactory:
    def __init__(
            self,
            repo_factory: repository.RepoFactory,
            *,
            current_user: BaseUser,
            config: Config,
    ):
        self._repo = repo_factory
        self._current_user = current_user
        self._config = config

    @property
    def kanban(self) -> KanbanApplicationService:
        return KanbanApplicationService(
            self._current_user,
            column_repo=self._repo.column,
            task_repo=self._repo.task,
            is_user_in_project=lambda project_id, user_id: is_user_in_project(
                project_id=project_id,
                user_id=user_id,
                project_service_conn=(
                    self._config.PROJECT_SERVICE_GRPC.HOST,
                    self._config.PROJECT_SERVICE_GRPC.PORT,
                ),
            ),
        )

    @property
    def stats(self) -> StatsApplicationService:
        return StatsApplicationService(config=self._config)

    @property
    def permission(self) -> PermissionApplicationService:
        return PermissionApplicationService()
