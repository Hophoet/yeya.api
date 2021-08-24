from datetime import datetime
from fastapi import File, UploadFile
from pydantic import BaseModel, UUID4
from typing import Optional, List
from enum import Enum

from pydantic.utils import T
from .user import User
from .category import Category
from pydantic import UUID4, BaseModel, EmailStr, validator
from .geolocation import Geolocation, GeolocationCreate
from .city import City
from .job import Job, JobBD, JobCreate
from .user import User

class Proposal(BaseModel):
    id: str = None
    text: str
    created_at: Optional[datetime]
    job:Job
    user:User

class ProposalDB(BaseModel):
    id: Optional[str] = None
    text: str
    job_id: str
    user_id: str
    created_at:Optional[datetime] = datetime.now()

class CreateProposalSerializer(BaseModel):
    job_id: str
    text: str