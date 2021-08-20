from typing import Optional, List
from .user import User
from pydantic import BaseModel
from .job import Job

class Favorite(BaseModel):
    id: str 
    user: User
    jobs: List[Job]

class FavoriteDB(BaseModel):
    id: Optional[str] = None
    user_id: str 
    jobs_ids: List[str] = []

class ToggleJobFavorite(BaseModel):
    user_id: str
    job_id: str


class ToggleJobFavoriteSerializer(BaseModel):
    job_id: str