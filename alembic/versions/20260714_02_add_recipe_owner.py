"""Add an owner to every recipe.

Revision ID: 20260714_02
Revises: 20260714_01
Create Date: 2026-07-14
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "20260714_02"
down_revision: Union[str, Sequence[str], None] = "20260714_01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Batch mode works with SQLite, which recreates the table for this change.
    # It assumes the educational database is empty or was recreated before upgrade.
    with op.batch_alter_table("recipes", recreate="always") as batch_op:
        batch_op.add_column(sa.Column("owner_id", sa.Integer(), nullable=False))
        batch_op.create_index("ix_recipes_owner_id", ["owner_id"], unique=False)
        batch_op.create_foreign_key(
            "fk_recipes_owner_id_users", "users", ["owner_id"], ["id"]
        )


def downgrade() -> None:
    with op.batch_alter_table("recipes", recreate="always") as batch_op:
        batch_op.drop_constraint("fk_recipes_owner_id_users", type_="foreignkey")
        batch_op.drop_index("ix_recipes_owner_id")
        batch_op.drop_column("owner_id")
