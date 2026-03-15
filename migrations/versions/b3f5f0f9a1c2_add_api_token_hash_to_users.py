"""add api token hash to users

Revision ID: b3f5f0f9a1c2
Revises: 8f3f38f8d7d1
Create Date: 2026-03-16 03:25:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b3f5f0f9a1c2"
down_revision = "8f3f38f8d7d1"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("api_token_hash", sa.String(length=255), nullable=True))


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("api_token_hash")
