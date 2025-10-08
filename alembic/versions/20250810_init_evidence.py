from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg


revision = '0001_init_evidence'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
	op.create_table(
		'evidence',
		sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
		sa.Column('title', sa.Text(), nullable=True),
		sa.Column('etype', sa.String(length=50), nullable=False),
		sa.Column('payload', pg.JSONB(), nullable=False),
		sa.Column('status', sa.String(length=20), nullable=False, server_default='new'),
		sa.Column('provenance', pg.JSONB(), nullable=True),
		sa.Column('created_by', sa.String(length=100), nullable=False),
		sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
		sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
	)


	op.create_table(
		'render_artifact',
		sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
		sa.Column('evidence_id', pg.UUID(as_uuid=True), sa.ForeignKey('evidence.id', ondelete='CASCADE'), nullable=False),
		sa.Column('format', sa.String(length=10), nullable=False),
		sa.Column('width', sa.Integer(), nullable=True),
		sa.Column('height', sa.Integer(), nullable=True),
		sa.Column('dpi', sa.Integer(), nullable=True),
		sa.Column('content_hash', sa.String(length=128), nullable=False),
		sa.Column('path', sa.Text(), nullable=False),
		sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
		sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
		sa.UniqueConstraint('evidence_id', 'format', 'content_hash', name='uq_artifact_dedup')
	)
	op.create_index('ix_render_artifact_content_hash', 'render_artifact', ['content_hash'])




def downgrade():
	op.drop_index('ix_render_artifact_content_hash', table_name='render_artifact')
	op.drop_table('render_artifact')
	op.drop_table('evidence')