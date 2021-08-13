from typing import Optional
from pydantic import BaseModel

class Image(BaseModel):
    url:Optional[str] 
    name:Optional[str]