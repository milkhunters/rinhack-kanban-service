from enum import Enum


class UserState(int, Enum):
    NOT_CONFIRMED = 0
    ACTIVE = 1
    BLOCKED = 2
    DELETED = 3


class NotificationType(int, Enum):
    INFO = 1
