"""add invite codes for closed beta

Revision ID: 0f1c9f8e7a21
Revises: b3f5f0f9a1c2
Create Date: 2026-03-18 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0f1c9f8e7a21"
down_revision = "b3f5f0f9a1c2"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "invite_codes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("label", sa.String(length=120), nullable=True),
        sa.Column("max_uses", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("invite_code_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("invite_code_value", sa.String(length=64), nullable=True))
        batch_op.create_foreign_key("fk_users_invite_code_id", "invite_codes", ["invite_code_id"], ["id"])


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_constraint("fk_users_invite_code_id", type_="foreignkey")
        batch_op.drop_column("invite_code_value")
        batch_op.drop_column("invite_code_id")

    op.drop_table("invite_codes")
