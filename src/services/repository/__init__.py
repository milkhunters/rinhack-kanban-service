from .column import ColumnRepo
from .task import TaskRepo
from .tag import TagRepo


class RepoFactory:
    def __init__(self, session):
        self._session = session

    @property
    def column(self) -> ColumnRepo:
        return ColumnRepo(self._session)

    @property
    def task(self) -> TaskRepo:
        return TaskRepo(self._session)

    @property
    def tag(self) -> TagRepo:
        return TagRepo(self._session)
