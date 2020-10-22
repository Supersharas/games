"""empty message

Revision ID: 03d83d2daa10
Revises: b9564ba77d8d
Create Date: 2020-10-22 12:36:58.665055

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03d83d2daa10'
down_revision = 'b9564ba77d8d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('games_offer_id_fkey', 'games', type_='foreignkey')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key('games_offer_id_fkey', 'games', 'offers', ['offer_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    # ### end Alembic commands ###
