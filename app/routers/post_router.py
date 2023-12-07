# routers/post_router.py

from fastapi import APIRouter, Depends, Security
from typing import List, Annotated
from ..controllers.auth_controller import verify_and_get_current_user_id
from app.controllers.post_controller import (
    create_post,
    find_all_posts,
    find_one_post,
    update_post,
    delete_post,
)
from ..models.post import Post
from ..models.user import User, UserIdAndUsername

post_router = APIRouter(
    prefix="/posts",
    tags=["post"],
)

@post_router.post("", response_model=Post, description="Create a new post")
async def create_post_route(post: Post, user: Annotated[UserIdAndUsername, Security(verify_and_get_current_user_id, scopes=["User"])]):
    return await create_post(post, user)

@post_router.get("", response_model=List[Post], description="Get all posts")
async def get_all_posts_route():
    return await find_all_posts()

@post_router.get("/one", response_model=Post, description="Get one post")
async def get_post_route():
    return await find_one_post()

@post_router.put("/{post_id}", response_model=Post, description="Update a post by ID")
async def update_post_route(post_id: int, post: Post, user: Annotated[UserIdAndUsername, Security(verify_and_get_current_user_id, scopes=["User"])]):
    return await update_post(post_id, post, user)

@post_router.delete("/{post_id}", response_model=dict, description="Delete a post by ID")
async def delete_post_route(post_id: int, user: Annotated[UserIdAndUsername, Security(verify_and_get_current_user_id, scopes=["User"])]):
    return await delete_post(post_id, user)
