"""added new fields

Revision ID: 4369f2ccf446
Revises: 9169d471b013
Create Date: 2023-11-26 00:10:50.952737

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4369f2ccf446'
down_revision: Union[str, None] = '9169d471b013'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tags',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('title', sa.VARCHAR(length=32), nullable=False),
    sa.Column('project_id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('task_tags',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('task_id', sa.UUID(), nullable=False),
    sa.Column('tag_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('columns', sa.Column('wip_limit', sa.INTEGER(), nullable=True))
    op.add_column('tasks', sa.Column('story_point', sa.INTEGER(), nullable=False))
    op.add_column('tasks', sa.Column('start_time', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tasks', sa.Column('end_time', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tasks', sa.Column('executor_id', sa.UUID(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tasks', 'executor_id')
    op.drop_column('tasks', 'end_time')
    op.drop_column('tasks', 'start_time')
    op.drop_column('tasks', 'story_point')
    op.drop_column('columns', 'wip_limit')
    op.drop_table('task_tags')
    op.drop_table('tags')
    # ### end Alembic commands ###
