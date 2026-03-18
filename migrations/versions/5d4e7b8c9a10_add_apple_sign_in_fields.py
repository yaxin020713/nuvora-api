"""add apple sign in fields

Revision ID: 5d4e7b8c9a10
Revises: 0f1c9f8e7a21
Create Date: 2026-03-18 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5d4e7b8c9a10"
down_revision = "0f1c9f8e7a21"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.alter_column("password_hash", existing_type=sa.String(length=255), nullable=True)
        batch_op.add_column(sa.Column("auth_provider", sa.String(length=30), nullable=False, server_default="local"))
        batch_op.add_column(sa.Column("provider_subject", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("email", sa.String(length=255), nullable=True))
        batch_op.create_unique_constraint("uq_users_provider_subject", ["provider_subject"])


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_constraint("uq_users_provider_subject", type_="unique")
        batch_op.drop_column("email")
        batch_op.drop_column("provider_subject")
        batch_op.drop_column("auth_provider")
        batch_op.alter_column("password_hash", existing_type=sa.String(length=255), nullable=False)
