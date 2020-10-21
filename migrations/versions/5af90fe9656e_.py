"""empty message

Revision ID: 5af90fe9656e
Revises: 1b01bf1b8582
Create Date: 2020-10-20 11:23:58.088768

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5af90fe9656e'
down_revision = '1b01bf1b8582'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('offers_player_two_fkey', 'offers', type_='foreignkey')
    op.drop_column('offers', 'player_two')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('offers', sa.Column('player_two', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('offers_player_two_fkey', 'offers', 'players', ['player_two'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    # ### end Alembic commands ###