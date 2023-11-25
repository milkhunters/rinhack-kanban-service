import uuid

from sqlalchemy import UUID, VARCHAR, DateTime, func, ForeignKey, INT
from sqlalchemy import Column as SAColumn
from sqlalchemy.orm import relationship

from src.db import Base


class Task(Base):
    """
    The Task model
    """
    __tablename__ = "tasks"

    id = SAColumn(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = SAColumn(VARCHAR(64), nullable=False)
    content = SAColumn(VARCHAR(10000), nullable=True)
    color = SAColumn(VARCHAR(7), nullable=False)
    story_point = SAColumn(INT, nullable=False)
    start_time = SAColumn(DateTime(timezone=True), nullable=True)
    end_time = SAColumn(DateTime(timezone=True), nullable=True)
    executor_id = SAColumn(UUID(as_uuid=True), nullable=True)
    column_id = SAColumn(UUID(as_uuid=True), ForeignKey('columns.id', ondelete='CASCADE'), nullable=False)
    column = relationship("models.tables.column.Column", back_populates="tasks")
    tags = relationship('models.tables.tag.Tag', secondary='task_tags', back_populates='tasks')
    child_id = SAColumn(UUID(as_uuid=True), nullable=True)

    created_at = SAColumn(DateTime(timezone=True), server_default=func.now())
    updated_at = SAColumn(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'


class TaskTag(Base):
    """
    Many-to-many table for Task and Tag
    """
    __tablename__ = "task_tags"

    id = SAColumn(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = SAColumn(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    tag_id = SAColumn(UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'
