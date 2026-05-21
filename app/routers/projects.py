import math
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import ProjectPlace, TravelProject
from app.schemas import PaginatedProjects, ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.art_institute import get_artwork

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    places_input = payload.places or []

    if len(places_input) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 places per project")

    external_ids = [p.external_id for p in places_input]
    if len(external_ids) != len(set(external_ids)):
        raise HTTPException(status_code=400, detail="Duplicate external_id values in places list")

    artwork_cache: dict = {}
    for place in places_input:
        artwork = await get_artwork(place.external_id)
        if artwork is None:
            raise HTTPException(
                status_code=404,
                detail=f"Artwork id={place.external_id} not found in Art Institute of Chicago API",
            )
        artwork_cache[place.external_id] = artwork

    project = TravelProject(
        name=payload.name,
        description=payload.description,
        start_date=payload.start_date,
    )
    db.add(project)
    db.flush()

    for place in places_input:
        artwork = artwork_cache[place.external_id]
        db.add(ProjectPlace(
            project_id=project.id,
            external_id=place.external_id,
            title=artwork.get("title"),
            artist_display=artwork.get("artist_display"),
        ))

    db.commit()
    db.refresh(project)
    return project


@router.get("/", response_model=PaginatedProjects)
def list_projects(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    status: Optional[str] = Query(default=None, description="Filter by status: active | completed"),
    db: Session = Depends(get_db),
):
    all_projects = db.query(TravelProject).order_by(TravelProject.created_at.desc()).all()

    if status in ("active", "completed"):
        all_projects = [p for p in all_projects if p.status == status]

    total = len(all_projects)
    start = (page - 1) * limit
    items = all_projects[start: start + limit]

    return PaginatedProjects(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=math.ceil(total / limit) if total > 0 else 0,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(TravelProject).filter(TravelProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(TravelProject).filter(TravelProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(TravelProject).filter(TravelProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    if any(p.visited for p in project.places):
        raise HTTPException(status_code=400, detail="Cannot delete a project that has visited places")

    db.delete(project)
    db.commit()
