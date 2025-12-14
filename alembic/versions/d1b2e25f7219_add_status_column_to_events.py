"""add status column to events

Revision ID: d1b2e25f7219
Revises: 
Create Date: 2025-12-14 20:32:20.209533

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'd1b2e25f7219'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add status column to events table
    op.add_column('events', sa.Column('status', sa.String(), server_default='upcoming', nullable=True))

def downgrade() -> None:
    # Remove status column from events table
    op.drop_column('events', 'status')
