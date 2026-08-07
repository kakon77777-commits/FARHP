"""FARHP v0.9 baseline schema."""
from alembic import op
import sqlalchemy as sa
revision = "0001_v09_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(80), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(32), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_role", "users", ["role"])
    op.create_table("research_plans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("study_id", sa.String(128), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(24), nullable=False, server_default="draft"),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("fingerprint_algorithm", sa.String(32)),
        sa.Column("fingerprint_value", sa.String(128)),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("locked_at", sa.DateTime(timezone=True)),
        sa.Column("previous_plan_id", sa.Integer(), sa.ForeignKey("research_plans.id")),
        sa.UniqueConstraint("study_id", "revision", name="uq_plan_study_revision"),
    )
    op.create_index("ix_research_plans_study_id", "research_plans", ["study_id"])
    op.create_index("ix_research_plans_status", "research_plans", ["status"])
    op.create_index("ix_research_plans_fingerprint_value", "research_plans", ["fingerprint_value"])
    op.create_table("preregistration_archives",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("plan_id", sa.Integer(), sa.ForeignKey("research_plans.id"), nullable=False, unique=True),
        sa.Column("archive_digest", sa.String(64), nullable=False, unique=True),
        sa.Column("archive_json", sa.Text(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table("invites",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(80), nullable=False),
        sa.Column("plan_id", sa.Integer(), sa.ForeignKey("research_plans.id"), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("max_uses", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("uses", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_invites_code", "invites", ["code"], unique=True)
    op.create_index("ix_invites_plan_id", "invites", ["plan_id"])
    op.create_table("study_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.String(96), nullable=False),
        sa.Column("plan_id", sa.Integer(), sa.ForeignKey("research_plans.id"), nullable=False),
        sa.Column("invite_id", sa.Integer(), sa.ForeignKey("invites.id"), nullable=False),
        sa.Column("participant_code", sa.String(96), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="consented"),
        sa.Column("consent_json", sa.Text(), nullable=False),
        sa.Column("checkpoint_json", sa.Text()),
        sa.Column("study_json", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_study_sessions_session_id", "study_sessions", ["session_id"], unique=True)
    op.create_index("ix_study_sessions_plan_id", "study_sessions", ["plan_id"])
    op.create_index("ix_study_sessions_invite_id", "study_sessions", ["invite_id"])
    op.create_index("ix_study_sessions_participant_code", "study_sessions", ["participant_code"])
    op.create_index("ix_study_sessions_status", "study_sessions", ["status"])
    op.create_table("audit_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entity_type", sa.String(32), nullable=False),
        sa.Column("entity_id", sa.String(128), nullable=False),
        sa.Column("event_index", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("prev_hash", sa.String(64), nullable=False),
        sa.Column("event_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("entity_type", "entity_id", "event_index", name="uq_audit_entity_index"),
    )
    op.create_index("ix_audit_events_entity_type", "audit_events", ["entity_type"])
    op.create_index("ix_audit_events_entity_id", "audit_events", ["entity_id"])


def downgrade():
    op.drop_table("audit_events")
    op.drop_table("study_sessions")
    op.drop_table("invites")
    op.drop_table("preregistration_archives")
    op.drop_table("research_plans")
    op.drop_table("users")
