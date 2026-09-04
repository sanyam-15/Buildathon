"""Audit log, agent run, and agent action models."""

from sqlalchemy import Column, String, DateTime, JSON, Text
from sqlalchemy.sql import func
from app.database.database import Base
import uuid


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    recovery_case_id = Column(String, nullable=False, index=True)
    event_type = Column(String, nullable=False)
    agent_name = Column(String, nullable=True)
    message = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    timestamp = Column(DateTime, server_default=func.now())


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    recovery_case_id = Column(String, nullable=False, index=True)
    agent_name = Column(String, nullable=False)
    status = Column(String, default="running")  # running, completed, failed
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)


class AgentAction(Base):
    __tablename__ = "agent_actions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    recovery_case_id = Column(String, nullable=False, index=True)
    agent_name = Column(String, nullable=False)
    action_type = Column(String, nullable=False)  # tool_call, decision, finding
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    status = Column(String, default="completed")
    timestamp = Column(DateTime, server_default=func.now())


class Communication(Base):
    __tablename__ = "communications"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    recovery_case_id = Column(String, nullable=False, index=True)
    channel = Column(String, nullable=False)  # email, whatsapp, sms
    recipient = Column(String, nullable=False)
    subject = Column(String, nullable=True)
    message = Column(Text, nullable=False)
    status = Column(String, default="sent")  # sent, delivered, failed
    sent_at = Column(DateTime, server_default=func.now())
