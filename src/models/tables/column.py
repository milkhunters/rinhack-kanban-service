import uuid

from sqlalchemy import UUID, VARCHAR, DateTime, func
from sqlalchemy import Column as SAColumn
from sqlalchemy.orm import relationship

from src.db import Base


class Column(Base):
    """
    The Column model
    """
    __tablename__ = "columns"

    id = SAColumn(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = SAColumn(VARCHAR(64), nullable=False)
    project_id = SAColumn(UUID(as_uuid=True), nullable=False)
    tasks = relationship("models.tables.task.Task", back_populates="column")
    child_id = SAColumn(UUID(as_uuid=True), nullable=True)

    created_at = SAColumn(DateTime(timezone=True), server_default=func.now())
    updated_at = SAColumn(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'
