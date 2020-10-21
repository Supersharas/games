"""empty message

Revision ID: 5b5e9867227f
Revises: 598626733784
Create Date: 2020-10-21 20:25:36.542051

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b5e9867227f'
down_revision = '598626733784'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('games', sa.Column('offer_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'games', 'offers', ['offer_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'games', type_='foreignkey')
    op.drop_column('games', 'offer_id')
    # ### end Alembic commands ###
