"""db launch

Revision ID: 4160ea7d3dee
Revises: 
Create Date: 2022-06-23 11:56:37.994134

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4160ea7d3dee'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('feedback',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('message', sa.String(), nullable=True),
    sa.Column('date_time', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ingredients',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('iptracker',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ipaddress', sa.String(), nullable=True),
    sa.Column('city', sa.String(), nullable=True),
    sa.Column('country', sa.String(), nullable=True),
    sa.Column('date_time', sa.DateTime(), nullable=True),
    sa.Column('action', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('recipes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('recipe', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('password', sa.String(), nullable=True),
    sa.Column('uuid', sa.String(), nullable=True),
    sa.Column('registered_date', sa.DateTime(), nullable=True),
    sa.Column('current_login', sa.DateTime(), nullable=True),
    sa.Column('last_login', sa.DateTime(), nullable=True),
    sa.Column('userpic', sa.String(), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('name')
    )
    op.create_table('recipe_feedback',
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.Column('feedback_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['feedback_id'], ['feedback.id'], ),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ),
    sa.PrimaryKeyConstraint('recipe_id', 'feedback_id')
    )
    op.create_table('recipe_ingredients',
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.Column('ingredient_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ),
    sa.PrimaryKeyConstraint('recipe_id', 'ingredient_id')
    )
    op.create_table('user_feedback',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('feedback_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['feedback_id'], ['feedback.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'feedback_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_feedback')
    op.drop_table('recipe_ingredients')
    op.drop_table('recipe_feedback')
    op.drop_table('users')
    op.drop_table('recipes')
    op.drop_table('iptracker')
    op.drop_table('ingredients')
    op.drop_table('feedback')
    # ### end Alembic commands ###
