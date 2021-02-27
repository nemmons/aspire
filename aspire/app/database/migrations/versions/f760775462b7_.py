"""empty message

Revision ID: f760775462b7
Revises: 9611191a3d83
Create Date: 2021-02-26 15:36:33.772855

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f760775462b7'
down_revision = '9611191a3d83'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('rating_variables', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sub_risk_label', sa.String(length=25), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('rating_variables', schema=None) as batch_op:
        batch_op.drop_column('sub_risk_label')

    # ### end Alembic commands ###
