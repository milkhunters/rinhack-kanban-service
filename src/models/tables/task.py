import uuid

from sqlalchemy import UUID, VARCHAR, DateTime, func, ForeignKey
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
    column_id = SAColumn(UUID(as_uuid=True), ForeignKey('columns.id'), nullable=False)
    column = relationship("models.tables.column.Column", back_populates="tasks")
    child_id = SAColumn(UUID(as_uuid=True), nullable=True)

    created_at = SAColumn(DateTime(timezone=True), server_default=func.now())
    updated_at = SAColumn(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'
