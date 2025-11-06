"""add_cascade_delete_for_expenses

Revision ID: aecf5cebd673
Revises: 001
Create Date: 2025-11-06 20:30:28.671847+08:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aecf5cebd673'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 删除现有的外键约束
    op.drop_constraint('expenses_ibfk_1', 'expenses', type_='foreignkey')
    
    # 重新创建外键约束，添加 CASCADE DELETE
    op.create_foreign_key(
        'expenses_ibfk_1',
        'expenses', 'travel_plans',
        ['travel_plan_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # 删除带 CASCADE 的外键约束
    op.drop_constraint('expenses_ibfk_1', 'expenses', type_='foreignkey')
    
    # 恢复原来的外键约束（不带 CASCADE）
    op.create_foreign_key(
        'expenses_ibfk_1',
        'expenses', 'travel_plans',
        ['travel_plan_id'], ['id']
    )