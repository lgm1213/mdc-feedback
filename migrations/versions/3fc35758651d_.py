"""empty message

Revision ID: 3fc35758651d
Revises: None
Create Date: 2015-10-20 10:42:54.887329

"""

# revision identifiers, used by Alembic.
revision = '3fc35758651d'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('survey',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('source_id', sa.String(length=50), nullable=False),
    sa.Column('lang', sa.String(length=2), nullable=False),
    sa.Column('method', sa.String(length=3), nullable=False),
    sa.Column('date_submitted', sa.DateTime(), nullable=False),
    sa.Column('role', sa.Integer(), nullable=False),
    sa.Column('purpose', sa.Integer(), nullable=False),
    sa.Column('purpose_other', sa.String(length=200), nullable=True),
    sa.Column('route', sa.Integer(), nullable=True),
    sa.Column('rating', sa.Integer(), nullable=False),
    sa.Column('get_done', sa.Boolean(), nullable=True),
    sa.Column('best', sa.Integer(), nullable=True),
    sa.Column('best_other', sa.String(length=200), nullable=True),
    sa.Column('worst', sa.Integer(), nullable=True),
    sa.Column('worst_other', sa.String(length=200), nullable=True),
    sa.Column('improvement', sa.String(length=200), nullable=True),
    sa.Column('follow_up', sa.Boolean(), nullable=True),
    sa.Column('contact', sa.String(length=50), nullable=True),
    sa.Column('more_comments', sa.String(length=2000), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_survey_date_submitted'), 'survey', ['date_submitted'], unique=False)
    op.create_index(op.f('ix_survey_id'), 'survey', ['id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=80), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('full_name', sa.String(length=60), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_survey_id'), table_name='survey')
    op.drop_index(op.f('ix_survey_date_submitted'), table_name='survey')
    op.drop_table('survey')
    op.drop_table('roles')
    ### end Alembic commands ###
