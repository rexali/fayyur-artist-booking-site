"""data types  migration

Revision ID: 8b886afdf40b
Revises: 70956ab188d4
Create Date: 2022-07-13 21:24:20.024626

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b886afdf40b'
down_revision = '70956ab188d4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('artists', 'genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('venues', 'genres',
               existing_type=sa.VARCHAR(length=500),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('venues', 'genres',
               existing_type=sa.VARCHAR(length=500),
               nullable=True)
    op.alter_column('artists', 'genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    # ### end Alembic commands ###