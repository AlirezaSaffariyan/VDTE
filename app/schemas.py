from datetime import datetime
from typing import Any, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel


# --- User Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    password: str


# --- Template Schemas ---
class MenuItemCreate(BaseModel):
    id: str
    name: str
    flag: str
    style: dict[str, Any]


class TemplateDataCreate(BaseModel):
    rows: int
    cols: int
    paperSize: str
    orientation: str
    customWidth: Optional[int] = None
    customHeight: Optional[int] = None
    background_image: Optional[str] = None
    menu_items: List[dict[str, Any]]


class TemplateCreate(BaseModel):
    name: str
    sub_template_types: List[str]
    data: TemplateDataCreate


# --- Response Schemas ---
class TemplateVersionResponse(BaseModel):
    id: UUID
    version: int
    created_at: datetime


class TemplateVersionDetailedResponse(BaseModel):
    id: UUID
    version: int
    created_at: datetime
    data: dict[str, Any]


class TemplateResponse(BaseModel):
    id: UUID
    name: str
    sub_template_types: List[str]
    created_at: datetime
    latest_version: Union[TemplateVersionResponse, TemplateVersionDetailedResponse]


class TemplateVersionListResponse(BaseModel):
    id: UUID
    versions: List[TemplateVersionResponse]


# --- Update Metadata Schema ---
class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    sub_template_types: Optional[List[str]] = None
