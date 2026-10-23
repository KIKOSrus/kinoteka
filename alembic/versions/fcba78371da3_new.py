"""new

Revision ID: fcba78371da3
Revises: 9028d6c71f05
Create Date: 2026-10-09 14:26:26.702092

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fcba78371da3'
down_revision: Union[str, Sequence[str], None] = '9028d6c71f05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No-op: ограничения uq_* уже созданы в предыдущих миграциях.

    Автогенерация ошибочно предлагала создать их повторно, из-за чего
    `alembic upgrade head` падал на чистой БД.
    """
    pass


def downgrade() -> None:
    """No-op."""
    pass
