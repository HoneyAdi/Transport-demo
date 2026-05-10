"""Add POD dashboard tables

Revision ID: pod_dashboard_001
Revises: b676b2f11a78
Create Date: 2024-01-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'pod_dashboard_001'
down_revision = 'b676b2f11a78'
branch_labels = None
depends_on = None

def upgrade():
    # Create pod_status table
    op.create_table('pod_status',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('status_code', sa.String(length=20), nullable=False),
        sa.Column('status_name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('color_code', sa.String(length=10), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('status_code'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'])
    )
    
    # Create pod_tracking table
    op.create_table('pod_tracking',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transport_bill_id', sa.Integer(), nullable=False),
        sa.Column('status_code', sa.String(length=20), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['status_code'], ['pod_status.status_code']),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['transport_bill_id'], ['transport_bills.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_pod_status', 'pod_tracking', ['status_code'])
    op.create_index('idx_pod_timestamp', 'pod_tracking', ['timestamp'])
    op.create_index('idx_pod_tenant', 'pod_tracking', ['tenant_id'])
    
    # Insert default POD statuses
    op.execute("""
        INSERT INTO pod_status (status_code, status_name, description, color_code, is_default, tenant_id) 
        SELECT 'pending', 'Pending', 'POD pending submission', '#ffc107', TRUE, id FROM tenants
    """)
    
    op.execute("""
        INSERT INTO pod_status (status_code, status_name, description, color_code, is_default, tenant_id) 
        SELECT 'submitted', 'Submitted', 'POD submitted for review', '#17a2b8', FALSE, id FROM tenants
    """)
    
    op.execute("""
        INSERT INTO pod_status (status_code, status_name, description, color_code, is_default, tenant_id) 
        SELECT 'verified', 'Verified', 'POD verified by admin', '#28a745', FALSE, id FROM tenants
    """)
    
    op.execute("""
        INSERT INTO pod_status (status_code, status_name, description, color_code, is_default, tenant_id) 
        SELECT 'rejected', 'Rejected', 'POD rejected - requires resubmission', '#dc3545', FALSE, id FROM tenants
    """)
    
    op.execute("""
        INSERT INTO pod_status (status_code, status_name, description, color_code, is_default, tenant_id) 
        SELECT 'completed', 'Completed', 'POD process completed', '#007bff', FALSE, id FROM tenants
    """)

def downgrade():
    op.drop_index('idx_pod_tenant', table_name='pod_tracking')
    op.drop_index('idx_pod_timestamp', table_name='pod_tracking')
    op.drop_index('idx_pod_status', table_name='pod_tracking')
    op.drop_table('pod_tracking')
    op.drop_table('pod_status')
