"""make email required for local auth

Revision ID: 9ab3c4d5e6f7
Revises: 5d4e7b8c9a10
Create Date: 2026-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9ab3c4d5e6f7"
down_revision = "5d4e7b8c9a10"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.create_unique_constraint("uq_users_email", ["email"])


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_constraint("uq_users_email", type_="unique")
