"""add_current_location_to_campaigns

Revision ID: 507644a1afc5
Revises: dd45f2fac9ea
Create Date: 2025-12-25 15:54:56.405922

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '507644a1afc5'
down_revision = 'dd45f2fac9ea'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add current_location column to mythweaver_campaigns table
    op.add_column('mythweaver_campaigns',
        sa.Column('current_location', sa.String(200), nullable=True, server_default='The Crossroads Inn')
    )


def downgrade() -> None:
    # Remove current_location column
    op.drop_column('mythweaver_campaigns', 'current_location')