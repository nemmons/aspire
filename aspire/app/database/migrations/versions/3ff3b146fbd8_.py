"""empty message

Revision ID: 3ff3b146fbd8
Revises: 150fed6b4ab3
Create Date: 2020-11-29 22:15:20.376615

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ff3b146fbd8'
down_revision = '150fed6b4ab3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('rating_steps', schema=None) as batch_op:
        batch_op.add_column(sa.Column('conditions', sa.String(length=512), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('rating_steps', schema=None) as batch_op:
        batch_op.drop_column('conditions')
    # ### end Alembic commands ###
