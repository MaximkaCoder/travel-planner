from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class TravelProject(Base):
    __tablename__ = "travel_projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    places = relationship("ProjectPlace", back_populates="project", cascade="all, delete-orphan", lazy="select")

    @property
    def status(self) -> str:
        if not self.places:
            return "active"
        return "completed" if all(p.visited for p in self.places) else "active"


class ProjectPlace(Base):
    __tablename__ = "project_places"
    __table_args__ = (UniqueConstraint("project_id", "external_id", name="uq_project_external_id"),)

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("travel_projects.id", ondelete="CASCADE"), nullable=False)
    external_id = Column(Integer, nullable=False, index=True)
    title = Column(String(500), nullable=True)
    artist_display = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    visited = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("TravelProject", back_populates="places")
