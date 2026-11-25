"""add warehouse code to sales orders

Revision ID: b075347a0331
Revises: 30c3216cef99
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b075347a0331"
down_revision: str | Sequence[str] | None = "30c3216cef99"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "sales_orders",
        sa.Column(
            "warehouse_code",
            sa.String(length=50),
            nullable=False,
            server_default="MAIN",
        ),
    )

    # Remove the temporary database-level default.
    op.alter_column(
        "sales_orders",
        "warehouse_code",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_column(
        "sales_orders",
        "warehouse_code",
    )
