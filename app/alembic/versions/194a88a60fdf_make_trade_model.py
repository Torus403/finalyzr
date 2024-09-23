"""make Trade model

Revision ID: 194a88a60fdf
Revises: 18dd272019ad
Create Date: 2024-09-23 15:19:48.623624

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '194a88a60fdf'
down_revision: Union[str, None] = '18dd272019ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('trades',
    sa.Column('id', mysql.CHAR(length=36), nullable=False),
    sa.Column('action', sa.Enum('BUY', 'SELL', name='actiontype', native_enum=False), nullable=False),
    sa.Column('execution_timestamp', sa.DateTime(timezone=True), nullable=False),
    sa.Column('ticker', sa.String(length=10), nullable=False),
    sa.Column('price', sa.Numeric(precision=20, scale=10), nullable=False),
    sa.Column('quantity', sa.Numeric(precision=20, scale=10), nullable=False),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('notes', sa.String(length=1000), nullable=True),
    sa.Column('portfolio_id', mysql.CHAR(length=36), nullable=False),
    sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trades_id'), 'trades', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_trades_id'), table_name='trades')
    op.drop_table('trades')
    # ### end Alembic commands ###
