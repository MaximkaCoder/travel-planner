from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class PlaceCreate(BaseModel):
    external_id: int = Field(..., gt=0, description="Art Institute of Chicago artwork ID")


class PlaceUpdate(BaseModel):
    notes: Optional[str] = Field(default=None, max_length=5000)
    visited: Optional[bool] = None


class PlaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    external_id: int
    title: Optional[str] = None
    artist_display: Optional[str] = None
    notes: Optional[str] = None
    visited: bool
    created_at: datetime
    updated_at: datetime


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    start_date: Optional[date] = None
    places: Optional[List[PlaceCreate]] = Field(default=None, max_length=10)


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    start_date: Optional[date] = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    status: str
    created_at: datetime
    updated_at: datetime
    places: List[PlaceResponse] = []


class PaginatedProjects(BaseModel):
    items: List[ProjectResponse]
    total: int
    page: int
    limit: int
    pages: int
