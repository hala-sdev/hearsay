import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Text, DateTime, CheckConstraint, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Check(Base):
    __tablename__ = "checks"

    check_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[str] = mapped_column(Text, server_default="queued")
    error: Mapped[str | None] = mapped_column(Text)
    total_claims:  Mapped[int | None] = mapped_column()
    client_ip: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (
        CheckConstraint("status IN ('queued', 'running', 'done', 'error')", name="status_check"),
    )

class Claim(Base):
    __tablename__ = "claims"

    check_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("checks.check_id"), primary_key=True)
    claim_index: Mapped[int] = mapped_column(primary_key=True)
    claim: Mapped[str] = mapped_column(Text)
    label: Mapped[str] = mapped_column(Text)
    reasoning: Mapped[str] = mapped_column(Text)
    cited: Mapped[list] = mapped_column(JSONB, server_default="[]")
    retried: Mapped[bool] = mapped_column(server_default="false")
    first_pass: Mapped[str|None] = mapped_column(Text)
    warnings: Mapped[dict] = mapped_column(JSONB)
    __table_args__ = (
        CheckConstraint("label IN ('SUPPORTS', 'REFUTES', 'NOT ENOUGH INFO', 'ERROR')", name="label_check"),
    )