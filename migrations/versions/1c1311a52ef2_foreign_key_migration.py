"""foreign key  migration

Revision ID: 1c1311a52ef2
Revises: 8f34a47b9e2b
Create Date: 2022-06-30 19:31:25.740973

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1c1311a52ef2'
down_revision = '8f34a47b9e2b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('artists_venue_id_fkey', 'artists', type_='foreignkey')
    op.drop_constraint('artists_show_id_fkey', 'artists', type_='foreignkey')
    op.create_foreign_key(None, 'artists', 'venues', ['venue_id'], ['id'])
    op.drop_column('artists', 'show_id')
    op.drop_constraint('shows_venue_id_fkey', 'shows', type_='foreignkey')
    op.drop_constraint('shows_artist_id_fkey', 'shows', type_='foreignkey')
    op.create_foreign_key(None, 'shows', 'venues', ['venue_id'], ['id'])
    op.create_foreign_key(None, 'shows', 'artists', ['artist_id'], ['id'])
    op.drop_constraint('venues_artist_id_fkey', 'venues', type_='foreignkey')
    op.drop_constraint('venues_show_id_fkey', 'venues', type_='foreignkey')
    op.drop_column('venues', 'artist_id')
    op.drop_column('venues', 'show_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venues', sa.Column('show_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('venues', sa.Column('artist_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('venues_show_id_fkey', 'venues', 'shows', ['show_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('venues_artist_id_fkey', 'venues', 'artists', ['artist_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint(None, 'shows', type_='foreignkey')
    op.drop_constraint(None, 'shows', type_='foreignkey')
    op.create_foreign_key('shows_artist_id_fkey', 'shows', 'artists', ['artist_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('shows_venue_id_fkey', 'shows', 'venues', ['venue_id'], ['id'], ondelete='CASCADE')
    op.add_column('artists', sa.Column('show_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'artists', type_='foreignkey')
    op.create_foreign_key('artists_show_id_fkey', 'artists', 'shows', ['show_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('artists_venue_id_fkey', 'artists', 'venues', ['venue_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###
