from typing import List
from fastapi import HTTPException, status
from ..database.db_session import get_db
from ..models.post import Post
from ..models.user import UserIdAndUsername
from datetime import datetime

db = get_db()

# Custom exception
class RecordNotFound(Exception):
    def __init__(self, message="Record not found"):
        self.message = message
        super().__init__(self.message)

# Function to create a new post
async def create_post(post: Post, user: UserIdAndUsername) -> Post:
    query = "INSERT INTO posts (title, content, created_at) VALUES ($1, $2, NOW()) RETURNING post_id;"
    try:
        result = await db.fetch_val(query, post.title, post.content)
        post.post_id = result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create the post. Please try again later. " + str(e),
        )
    query = "INSERT INTO post_user (post_id, user_id) VALUES ($1, $2);"
    try:
        await db.execute(query, post.post_id, user.user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create the post. Please try again later. " + str(e),
        )
    post.user_id = user.user_id
    post.username = user.username
    post.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return post


# Function to retrieve all posts
async def find_all_posts() -> List[Post]:
    query = "SELECT post_id, title, content, created_at, user_id, username FROM posts JOIN post_user USING (post_id) JOIN users USING (user_id) ORDER BY created_at DESC;"
    try: 
        result = await db.fetch_rows(query)
        if result is None:
            return [] 
        return [Post(post_id=row["post_id"], title=row["title"], content=row["content"], created_at=row["created_at"].strftime("%Y-%m-%d %H:%M:%S"), user_id=row["user_id"], username=row["username"]) for row in result]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve posts. Please try again later. " + str(e),
        )

# Function to retrieve a single post
async def find_one_post() -> Post:
    range = "LIMIT 1"
    query = "SELECT post_id, title, content, created_at, user_id, username FROM posts JOIN post_user USING (post_id) JOIN users USING (user_id) ORDER BY created_at DESC " + range + ";"
    try:
        result = await db.fetch_row(query)
        if result:
            return Post(post_id=result["post_id"], title=result["title"], content=result["content"], user_id=result["user_id"], username=result["username"], created_at=result["created_at"].strftime("%Y-%m-%d %H:%M:%S"))
        else:
            # Create placeholder post
            return Post(post_id=0, title="Prendre soin de l'environement", content="C'est important", user_id=0, username="Mike", created_at="2023-12-08 1:00:00")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve post. Please try again later. " + str(e),
        )

# Function to retrieve a post by ID
async def find_post_by_id(post_id: int) -> Post:
    query = "SELECT post_id, title, content, created_at, user_id, username FROM posts JOIN post_user USING (post_id) JOIN users USING (user_id) WHERE post_id = $1;"
    try:
        result = await db.fetch_row(query, post_id)
        if result:
            return Post(post_id=result["post_id"], title=result["title"], content=result["content"], user_id=result["user_id"], username=result["username"], created_at=result["created_at"].strftime("%Y-%m-%d %H:%M:%S"))
        else:
            raise RecordNotFound
    except RecordNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve post. Please try again later. " + str(e),
        )

# Function to update a post by ID
async def update_post(post_id: int, post: Post, user: UserIdAndUsername) -> Post:
    is_owner = await is_post_owner(post_id, user.user_id)
    if not is_owner:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You don't have permission to update this post",
        )
    query = "UPDATE posts SET title=$1, content=$2 WHERE post_id=$3;"
    try:
        result = await db.execute(query, post.title, post.content, post_id)
        if result == "UPDATE 1":
            return post
        raise RecordNotFound
    except RecordNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or you don't have permission to update it"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update post. Please try again later. " + str(e),
        )

# Function to delete a post by ID
async def delete_post(post_id: int, user: UserIdAndUsername):
    is_owner = await is_post_owner(post_id, user.user_id)
    if not is_owner:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You don't have permission to delete this post",
        )
    query = "DELETE FROM posts WHERE post_id = $1;"
    try:
        deleted_rows = await db.execute(query, post_id)
        if deleted_rows == "DELETE 1":
            return {"message": "Post deleted"}
        raise RecordNotFound
    except RecordNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or you don't have permission to delete it"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete post. Please try again later. " + str(e),
        )


# Function that takes a post id and a user id and returns True if the user is the owner of the post
async def is_post_owner(post_id: int, user_id: str) -> bool:
    query = "SELECT EXISTS(SELECT 1 FROM post_user WHERE post_id = $1 AND user_id = $2);"
    try:
        result = await db.fetch_val(query, post_id, user_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check if user is owner of post. Please try again later. " + str(e),
        )

