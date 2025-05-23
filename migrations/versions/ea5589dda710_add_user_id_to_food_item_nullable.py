"""add user_id to food_item nullable

Revision ID: ea5589dda710
Revises: d2205f63d6a9
Create Date: 2025-04-28 14:46:16.706855

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea5589dda710'
down_revision = 'd2205f63d6a9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("DROP TABLE IF EXISTS _alembic_tmp_food_item")
    with op.batch_alter_table('food_item', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_food_item_user_id'), ['user_id'], unique=False)
        batch_op.create_foreign_key('fk_fooditem_user_id', 'user', ['user_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('food_item', schema=None) as batch_op:
        batch_op.drop_constraint('fk_fooditem_user_id', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_food_item_user_id'))
        batch_op.drop_column('user_id')

    op.create_table('_alembic_tmp_food_item',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=100), nullable=False),
    sa.Column('serving_size', sa.FLOAT(), nullable=False),
    sa.Column('serving_unit', sa.VARCHAR(length=20), nullable=False),
    sa.Column('calories', sa.FLOAT(), nullable=False),
    sa.Column('protein', sa.FLOAT(), nullable=True),
    sa.Column('fat', sa.FLOAT(), nullable=True),
    sa.Column('carbs', sa.FLOAT(), nullable=True),
    sa.Column('category', sa.VARCHAR(length=50), nullable=True),
    sa.Column('source', sa.VARCHAR(length=50), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='fk_fooditem_user_id'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
