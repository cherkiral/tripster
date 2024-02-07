"""Initial migration3

Revision ID: b6d35d208877
Revises: 978fa2893f91
Create Date: 2024-02-06 20:09:56.635979

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b6d35d208877'
down_revision: Union[str, None] = '978fa2893f91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('num_votes', sa.Integer(), nullable=True))
    op.add_column('posts', sa.Column('rating', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'rating')
    op.drop_column('posts', 'num_votes')
    # ### end Alembic commands ###
