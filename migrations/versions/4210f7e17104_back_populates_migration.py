"""back_populates  migration

Revision ID: 4210f7e17104
Revises: 659fd2eed693
Create Date: 2022-07-02 15:29:10.689742

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4210f7e17104'
down_revision = '659fd2eed693'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('artists_show_id_fkey', 'artists', type_='foreignkey')
    op.drop_column('artists', 'show_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('show_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('artists_show_id_fkey', 'artists', 'shows', ['show_id'], ['id'])
    # ### end Alembic commands ###