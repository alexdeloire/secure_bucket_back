from fastapi import APIRouter, Security
from fastapi.responses import JSONResponse
from typing import Annotated

from ..controllers.auth_controller import verify_token
from ..controllers.user_controller import find_user_by_username, find_all_users, ban_user_by_username
from ..models.user import User


user_router = APIRouter(
    prefix="/users",
    tags=["user"]
)

@user_router.get("/{username}", response_model=User, description="Get a user by username")
async def get_user(username: str, token: Annotated[None, Security(verify_token, scopes=["Admin"])]):
    return await find_user_by_username(username)

@user_router.get("", response_model=list[User], description="Get all users")
async def get_all_users(token: Annotated[None, Security(verify_token, scopes=["Admin"])]):
    return await find_all_users()

@user_router.put("/{username}", response_model=dict, description="Ban a user by username")
async def ban_user(username: str, token: Annotated[None, Security(verify_token, scopes=["Admin"])]):
    return await ban_user_by_username(username)
