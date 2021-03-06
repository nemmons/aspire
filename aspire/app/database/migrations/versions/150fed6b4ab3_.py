"""empty message

Revision ID: 150fed6b4ab3
Revises: 34d99c094b7a
Create Date: 2020-11-24 23:07:15.786796

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '150fed6b4ab3'
down_revision = '34d99c094b7a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('rating_factors', schema=None) as batch_op:
        batch_op.add_column(sa.Column('rating_manual_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_rating_manual_id', 'rating_manuals', ['rating_manual_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('rating_factors', schema=None) as batch_op:
        batch_op.drop_constraint('fk_rating_manual_id', type_='foreignkey')
        batch_op.drop_column('rating_manual_id')
    # ### end Alembic commands ###
