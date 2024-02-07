from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PostCreate(BaseModel):
    title: str
    content: str

class PostRead(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    created_at: datetime
    num_votes: int
    rating: int

    class Config:
        orm_mode = True
