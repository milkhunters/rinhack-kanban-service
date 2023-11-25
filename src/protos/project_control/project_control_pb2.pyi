from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ProjectRequest(_message.Message):
    __slots__ = ["project_id", "user_id"]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    user_id: str
    def __init__(self, project_id: _Optional[str] = ..., user_id: _Optional[str] = ...) -> None: ...

class IsUserInProjectReply(_message.Message):
    __slots__ = ["result"]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: bool
    def __init__(self, result: bool = ...) -> None: ...

class CreateNotificationRequest(_message.Message):
    __slots__ = ["owner_id", "type_id", "content_id", "content"]
    OWNER_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_ID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    owner_id: str
    type_id: int
    content_id: str
    content: str
    def __init__(self, owner_id: _Optional[str] = ..., type_id: _Optional[int] = ..., content_id: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

class NotificationReply(_message.Message):
    __slots__ = ["id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...
