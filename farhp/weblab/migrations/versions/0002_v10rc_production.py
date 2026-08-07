"""FARHP v1.0 RC productionization fields and audit heads."""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone
revision = "0002_v10rc_production"
down_revision = "0001_v09_baseline"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("auth_provider", sa.String(255), nullable=False, server_default="local"))
        batch.add_column(sa.Column("external_subject", sa.String(255), nullable=True))
        batch.add_column(sa.Column("email", sa.String(320), nullable=True))
        batch.add_column(sa.Column("display_name", sa.String(255), nullable=True))
        batch.add_column(sa.Column("token_version", sa.Integer(), nullable=False, server_default="1"))
        batch.add_column(sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_users_auth_provider", "users", ["auth_provider"])
    op.create_index("uq_users_provider_subject", "users", ["auth_provider", "external_subject"], unique=True)
    op.create_table("audit_heads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entity_type", sa.String(32), nullable=False),
        sa.Column("entity_id", sa.String(128), nullable=False),
        sa.Column("next_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("head_hash", sa.String(64), nullable=False, server_default="0" * 64),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("entity_type", "entity_id", name="uq_audit_head_entity"),
    )
    conn = op.get_bind()
    rows = conn.execute(sa.text("""
        SELECT e.entity_type, e.entity_id, e.event_index, e.event_hash
        FROM audit_events e
        JOIN (
          SELECT entity_type, entity_id, MAX(event_index) AS max_index
          FROM audit_events GROUP BY entity_type, entity_id
        ) x ON x.entity_type=e.entity_type AND x.entity_id=e.entity_id AND x.max_index=e.event_index
    """)).mappings().all()
    now = datetime.now(timezone.utc)
    for row in rows:
        conn.execute(sa.text("INSERT INTO audit_heads (entity_type,entity_id,next_index,head_hash,updated_at) VALUES (:t,:i,:n,:h,:u)"),
                     {"t":row["entity_type"],"i":row["entity_id"],"n":row["event_index"]+1,"h":row["event_hash"],"u":now})


def downgrade():
    op.drop_table("audit_heads")
    op.drop_index("uq_users_provider_subject", table_name="users")
    op.drop_index("ix_users_auth_provider", table_name="users")
    with op.batch_alter_table("users") as batch:
        batch.drop_column("last_login_at")
        batch.drop_column("token_version")
        batch.drop_column("display_name")
        batch.drop_column("email")
        batch.drop_column("external_subject")
        batch.drop_column("auth_provider")
