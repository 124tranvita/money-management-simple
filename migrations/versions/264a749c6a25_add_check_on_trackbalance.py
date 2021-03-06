"""add check on TrackBalance

Revision ID: 264a749c6a25
Revises: 
Create Date: 2022-01-14 00:23:42.290385

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '264a749c6a25'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=64), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('profile_image', sa.String(length=64), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('wallets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=16), nullable=False),
    sa.Column('balance', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('filter', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('wallet_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['wallet_id'], ['wallets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('moneysaving',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('saving', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('wallet_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['wallet_id'], ['wallets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_moneysaving_date'), 'moneysaving', ['date'], unique=True)
    op.create_table('trackbalances',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('balance', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.Column('check', sa.Boolean(), nullable=True),
    sa.Column('wallet_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['wallet_id'], ['wallets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trackbalances_date'), 'trackbalances', ['date'], unique=True)
    op.create_table('expenditures',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('description', sa.String(length=128), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('wallet_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['wallet_id'], ['wallets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('expenditures')
    op.drop_index(op.f('ix_trackbalances_date'), table_name='trackbalances')
    op.drop_table('trackbalances')
    op.drop_index(op.f('ix_moneysaving_date'), table_name='moneysaving')
    op.drop_table('moneysaving')
    op.drop_table('items')
    op.drop_table('wallets')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
