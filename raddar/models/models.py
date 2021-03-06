import datetime

from pydantic import BaseModel
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
)
from sqlalchemy.orm import relationship

from ..db.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    name = Column(String, index=True)

    analyses = relationship("Analysis")


class Secret(Base):
    __tablename__ = "secrets"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    secret_type = Column(String, index=True)
    line_number = Column(Integer, index=True)
    secret_hashed = Column(String, index=True)

    analysis_id = Column(Integer, ForeignKey("analyses.id"))


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    execution_date = Column(DateTime, index=True)
    branch_name = Column(String)
    ref_name = Column(String)
    scan_origin = Column(String)

    project_id = Column(Integer, ForeignKey("projects.id"))

    secrets = relationship("Secret")


class GithubRepositoryPayload(BaseModel):
    id: int
    name: str
    full_name: str


class GitHubPushPayload(BaseModel):
    ref: str
    repository: GithubRepositoryPayload
