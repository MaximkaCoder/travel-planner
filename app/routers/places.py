from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import ProjectPlace, TravelProject
from app.schemas import PlaceCreate, PlaceResponse, PlaceUpdate
from app.services.art_institute import get_artwork

router = APIRouter(prefix="/projects/{project_id}/places", tags=["Places"])


def _get_project_or_404(project_id: int, db: Session) -> TravelProject:
    project = db.query(TravelProject).filter(TravelProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    return project


def _get_place_or_404(project_id: int, place_id: int, db: Session) -> ProjectPlace:
    place = db.query(ProjectPlace).filter(
        ProjectPlace.id == place_id,
        ProjectPlace.project_id == project_id,
    ).first()
    if not place:
        raise HTTPException(status_code=404, detail=f"Place {place_id} not found in project {project_id}")
    return place


@router.post("/", response_model=PlaceResponse, status_code=201)
async def add_place(project_id: int, payload: PlaceCreate, db: Session = Depends(get_db)):
    project = _get_project_or_404(project_id, db)

    if len(project.places) >= 10:
        raise HTTPException(status_code=400, detail="Project has reached the maximum of 10 places")

    duplicate = db.query(ProjectPlace).filter(
        ProjectPlace.project_id == project_id,
        ProjectPlace.external_id == payload.external_id,
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="This artwork is already added to the project")

    artwork = await get_artwork(payload.external_id)
    if artwork is None:
        raise HTTPException(
            status_code=404,
            detail=f"Artwork id={payload.external_id} not found in Art Institute of Chicago API",
        )

    place = ProjectPlace(
        project_id=project_id,
        external_id=payload.external_id,
        title=artwork.get("title"),
        artist_display=artwork.get("artist_display"),
    )
    db.add(place)
    db.commit()
    db.refresh(place)
    return place


@router.get("/", response_model=List[PlaceResponse])
def list_places(project_id: int, db: Session = Depends(get_db)):
    _get_project_or_404(project_id, db)
    return db.query(ProjectPlace).filter(ProjectPlace.project_id == project_id).all()


@router.get("/{place_id}", response_model=PlaceResponse)
def get_place(project_id: int, place_id: int, db: Session = Depends(get_db)):
    _get_project_or_404(project_id, db)
    return _get_place_or_404(project_id, place_id, db)


@router.patch("/{place_id}", response_model=PlaceResponse)
def update_place(project_id: int, place_id: int, payload: PlaceUpdate, db: Session = Depends(get_db)):
    _get_project_or_404(project_id, db)
    place = _get_place_or_404(project_id, place_id, db)

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    for field, value in update_data.items():
        setattr(place, field, value)

    place.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(place)
    return place
