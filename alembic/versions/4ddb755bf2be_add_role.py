"""add role

Revision ID: 4ddb755bf2be
Revises: 1e437b48c91d
Create Date: 2025-05-22 14:36:33.716238
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4ddb755bf2be"
down_revision: Union[str, None] = "1e437b48c91d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create ENUM type first
    user_role_enum = sa.Enum("admin", "student", name="userrole")
    user_role_enum.create(op.get_bind())

    # Add column using the new ENUM type
    op.add_column("users", sa.Column("role", user_role_enum, nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Drop column first
    op.drop_column("users", "role")

    # Then drop ENUM type
    sa.Enum(name="userrole").drop(op.get_bind())
