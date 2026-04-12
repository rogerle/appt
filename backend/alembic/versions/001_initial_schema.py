"""initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-04-11 00:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建 studios 表
    op.create_table('studios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建 instructors 表
    op.create_table('instructors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('studio_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['studio_id'], ['studios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建 schedules 表
    op.create_table('schedules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('instructor_id', sa.Integer(), nullable=False),
        sa.Column('studio_id', sa.Integer(), nullable=True),
        sa.Column('schedule_date', sa.Date(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('max_bookings', sa.Integer(), server_default='1', nullable=True),
        sa.Column('is_recurring', sa.Boolean(), server_default='false', nullable=True),
        sa.Column('recurrence_pattern', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['instructor_id'], ['instructors.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['studio_id'], ['studios.id']),
        sa.CheckConstraint('end_time > start_time', name='time_overlap'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建 bookings 表
    op.create_table('bookings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('schedule_id', sa.Integer(), nullable=False),
        sa.Column('customer_name', sa.String(length=50), nullable=False),
        sa.Column('customer_phone', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='confirmed', nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['schedule_id'], ['schedules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建 admins 表
    op.create_table('admins',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('studio_id', sa.Integer(), nullable=True),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['studio_id'], ['studios.id']),
        sa.UniqueConstraint('username'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index('idx_instructors_studio', 'instructors', ['studio_id'])
    op.create_index('idx_instructors_active', 'instructors', ['is_active'])
    op.create_index('idx_schedules_date', 'schedules', ['schedule_date'])
    op.create_index('idx_schedules_instructor', 'schedules', ['instructor_id'])
    op.create_index('idx_bookings_schedule', 'bookings', ['schedule_id'])
    op.create_index('idx_bookings_customer', 'bookings', ['customer_phone'])
    op.create_index('idx_bookings_status', 'bookings', ['status'])


def downgrade() -> None:
    # 删除索引
    op.drop_index('idx_bookings_status', table_name='bookings')
    op.drop_index('idx_bookings_customer', table_name='bookings')
    op.drop_index('idx_bookings_schedule', table_name='bookings')
    op.drop_index('idx_schedules_instructor', table_name='schedules')
    op.drop_index('idx_schedules_date', table_name='schedules')
    op.drop_index('idx_instructors_active', table_name='instructors')
    op.drop_index('idx_instructors_studio', table_name='instructors')
    
    # 删除表 (按依赖关系逆序)
    op.drop_table('admins')
    op.drop_table('bookings')
    op.drop_table('schedules')
    op.drop_table('instructors')
    op.drop_table('studios')
