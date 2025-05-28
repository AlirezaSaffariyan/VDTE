from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.security import get_current_user
from app.database import get_db
from app.models import Template, TemplateVersion, User
from app.schemas import (
    TemplateCreate,
    TemplateDataCreate,
    TemplateResponse,
    TemplateUpdate,
    TemplateVersionDetailedResponse,
    TemplateVersionListResponse,
    TemplateVersionResponse,
)

router = APIRouter(prefix="/templates", tags=["templates"])


# Create a new template
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_template(
    template: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Create Template (metadata)
    new_template = Template(
        user_id=current_user.id,
        name=template.name,
        sub_template_types=template.sub_template_types,
    )
    db.add(new_template)
    db.commit()
    db.refresh(new_template)

    # Create initial TemplateVersion (version=1)
    new_version = TemplateVersion(
        template_id=new_template.id,
        version=1,
        data=vars(template.data),  # Convert Pydantic model to dict for JSONB
    )
    db.add(new_version)
    db.commit()

    return {
        "id": str(new_template.id),
        "version": 1,
        "message": "Template created successfully",
    }


# Get all templates
@router.get("/", response_model=List[TemplateResponse])
def get_templates(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    templates = db.query(Template).filter(Template.user_id == current_user.id).all()
    result: List[TemplateResponse] = []

    for template in templates:
        template_latest_version = (
            db.query(TemplateVersion)
            .filter(TemplateVersion.template_id == template.id)
            .order_by(TemplateVersion.version.desc())
            .first()
        )

        result.append(
            TemplateResponse(
                id=template.id,
                name=template.name,
                sub_template_types=template.sub_template_types,
                created_at=template.created_at,
                latest_version=(
                    TemplateVersionResponse(
                        id=template_latest_version.id,
                        version=template_latest_version.version,
                        created_at=template_latest_version.created_at,
                    )
                    if template_latest_version
                    else None
                ),
            )
        )

    return result


# Get template by ID
@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(
    template_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    template = (
        db.query(Template)
        .filter(Template.id == template_id, Template.user_id == current_user.id)
        .first()
    )

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    latest_version = (
        db.query(TemplateVersion)
        .filter(TemplateVersion.template_id == template_id)
        .order_by(TemplateVersion.version.desc())
        .first()
    )

    return {**template.__dict__, "latest_version": latest_version.__dict__}


# Delete template
@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    template = (
        db.query(Template)
        .filter(Template.id == template_id, Template.user_id == current_user.id)
        .first()
    )

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    template_versions = (
        db.query(TemplateVersion)
        .filter(TemplateVersion.template_id == template_id)
        .all()
    )

    for template_version in template_versions:
        db.delete(template_version)

    db.delete(template)
    db.commit()


# Add new version
@router.post("/{template_id}/versions", status_code=201)
def add_version(
    template_id: UUID,
    data: TemplateDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify template exists and belongs to user
    template = (
        db.query(Template)
        .filter(Template.id == template_id, Template.user_id == current_user.id)
        .first()
    )
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Get latest version to increment
    latest_version = (
        db.query(TemplateVersion)
        .filter(TemplateVersion.template_id == template_id)
        .order_by(TemplateVersion.version.desc())
        .first()
    )

    new_version_number = latest_version.version + 1 if latest_version else 1

    # Create new version
    new_version = TemplateVersion(
        template_id=template_id, version=new_version_number, data=vars(data)
    )
    db.add(new_version)
    db.commit()

    return {"version": new_version_number}


# List all versions
@router.get("/{template_id}/versions", response_model=TemplateVersionListResponse)
def list_versions(
    template_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    template = (
        db.query(Template)
        .filter(Template.id == template_id, Template.user_id == current_user.id)
        .first()
    )
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    versions = (
        db.query(TemplateVersion)
        .filter(TemplateVersion.template_id == template_id)
        .order_by(TemplateVersion.version)
        .all()
    )

    template_versions: List[TemplateVersionResponse] = []
    for version in versions:
        template_versions.append(
            TemplateVersionResponse(
                id=version.id, version=version.version, created_at=version.created_at
            )
        )

    return {"id": template_id, "versions": versions}


# Get version by ID
@router.get(
    "/{template_id}/versions/{version_id}",
    response_model=TemplateVersionDetailedResponse,
)
def get_versions(
    template_id: UUID,
    version_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    template = (
        db.query(Template)
        .filter(Template.id == template_id, Template.user_id == current_user.id)
        .first()
    )
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    template_version = (
        db.query(TemplateVersion)
        .filter(
            TemplateVersion.template_id == template_id, TemplateVersion.id == version_id
        )
        .first()
    )

    return TemplateVersionDetailedResponse(
        id=template_version.id,
        version=template_version.version,
        created_at=template_version.created_at,
        data=template_version.data,
    )


# Update template metadata
@router.patch("/{template_id}/metadata")
def update_metadata(
    template_id: UUID,
    updates: TemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    template = (
        db.query(Template)
        .filter(Template.id == template_id, Template.user_id == current_user.id)
        .first()
    )
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Apply updates
    for field, value in vars(updates).items():
        setattr(template, field, value)

    db.commit()
    db.refresh(template)
    return template
