"""add_event_highlights_table

Revision ID: 32ef5da689f0
Revises: d1b2e25f7219
Create Date: 2025-12-15 18:55:58.763233

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '32ef5da689f0'
down_revision: Union[str, Sequence[str], None] = 'd1b2e25f7219'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create event_highlights table
    op.create_table(
        'event_highlights',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('embed_url', sa.String(), nullable=True),
        sa.Column('thumbnail', sa.String(), nullable=True),
        sa.Column('video_id', sa.String(), nullable=True),
        sa.Column('duration', sa.String(), nullable=True),
        sa.Column('platform', sa.String(), server_default='twitch', nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=True),
        sa.Column('highlight_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_event_highlights_id'), 'event_highlights', ['id'], unique=False)
    op.create_index(op.f('ix_event_highlights_event_id'), 'event_highlights', ['event_id'], unique=False)

def downgrade() -> None:
    # Drop event_highlights table
    op.drop_index(op.f('ix_event_highlights_event_id'), table_name='event_highlights')
    op.drop_index(op.f('ix_event_highlights_id'), table_name='event_highlights')
    op.drop_table('event_highlights')
