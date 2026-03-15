"""create health data table

Revision ID: 31240c1236d0
Revises: 
Create Date: 2026-03-16 02:34:42.389180

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '31240c1236d0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'health_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=50), nullable=False),
        sa.Column('heart_rate', sa.Integer(), nullable=True),
        sa.Column('water_intake', sa.Integer(), nullable=True),
        sa.Column('sleep_hours', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('health_data')
