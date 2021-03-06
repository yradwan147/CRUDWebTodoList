"""empty message

Revision ID: c9a800e58670
Revises: b3e48e206987
Create Date: 2021-02-19 20:02:52.520049

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9a800e58670'
down_revision = 'b3e48e206987'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('todos', sa.Column('completed', sa.Boolean(), nullable=True))
    
    
    #Altered manually
    op.execute('UPDATE todos SET completed = False WHERE completed IS NULL;')

    op.alter_column('todos', 'completed', nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('todos', 'completed')
    # ### end Alembic commands ###
