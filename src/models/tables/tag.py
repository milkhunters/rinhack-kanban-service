import uuid

from sqlalchemy import Column, UUID, VARCHAR, DateTime, func
from sqlalchemy.orm import relationship

from src.db import Base


class Tag(Base):
    """
    The Tag model

    """
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(VARCHAR(32), nullable=False)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    tasks = relationship("models.tables.task.Task", secondary='task_tags', back_populates='tags')

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'
