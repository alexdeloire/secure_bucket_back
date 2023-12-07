# models/post.py

from pydantic import BaseModel
from typing import Optional

class Post(BaseModel):
    post_id: Optional[int] = None
    title: str
    content: str
    user_id: Optional[int] = None
    username: Optional[str] = None
    created_at: Optional[str] = None

