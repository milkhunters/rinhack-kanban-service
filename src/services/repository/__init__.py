from .column import ColumnRepo
from .task import TaskRepo


class RepoFactory:
    def __init__(self, session):
        self._session = session

    @property
    def column(self) -> ColumnRepo:
        return ColumnRepo(self._session)

    @property
    def task(self) -> TaskRepo:
        return TaskRepo(self._session)
