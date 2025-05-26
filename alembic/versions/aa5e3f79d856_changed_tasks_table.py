"""Changed tasks table

Revision ID: aa5e3f79d856
Revises: 1e437b48c91d
Create Date: 2025-05-26 11:54:06.842239
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'aa5e3f79d856'
down_revision: Union[str, None] = '1e437b48c91d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    # Create the ENUM type
    user_role_enum = postgresql.ENUM('admin', 'student', name='userrole', create_type=True)
    user_role_enum.create(op.get_bind(), checkfirst=True)
    
    # Add the role column to the users table
    op.add_column('users', sa.Column('role', user_role_enum, nullable=True, default='student'))

def downgrade() -> None:
    """Downgrade schema."""
    # Drop the role column
    op.drop_column('users', 'role')
    
    # Drop the ENUM type
    op.execute("DROP TYPE IF EXISTS userrole")
