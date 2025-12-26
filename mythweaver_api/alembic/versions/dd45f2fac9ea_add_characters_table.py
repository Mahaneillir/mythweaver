"""add_characters_table

Revision ID: dd45f2fac9ea
Revises: 
Create Date: 2025-12-23 17:56:46.201086

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'dd45f2fac9ea'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create mythweaver_characters table
    op.create_table(
        'mythweaver_characters',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('origin', sa.String(50), nullable=False),
        sa.Column('path', sa.String(50), nullable=False),
        sa.Column('might_score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('agility_score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('wits_score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('presence_score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('current_hp', sa.Integer(), nullable=False),
        sa.Column('max_hp', sa.Integer(), nullable=False),
        sa.Column('current_focus', sa.Integer(), nullable=False),
        sa.Column('max_focus', sa.Integer(), nullable=False),
        sa.Column('supplies', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('skills', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('talents', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('bonds', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('inventory', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['campaign_id'], ['mythweaver_campaigns.id'], ondelete='CASCADE'),
    )


def downgrade() -> None:
    op.drop_table('mythweaver_characters')