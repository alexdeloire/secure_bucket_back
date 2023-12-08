from typing import List
from fastapi import HTTPException, status
from ..database.db_session import get_db
from ..models.user import User, UserIdAndUsername

db = get_db()


# Function to create a new user in the database
async def create_user(user: User):
    db = get_db()
    query = """
    INSERT INTO users (username, email, password, disabled)
    VALUES ($1, $2, $3, $4)
    RETURNING user_id;
    """
    user_id = await db.fetch_val(query, user.username, user.email, user.password, user.disabled)
    query = """
    INSERT INTO user_roles (user_id, role_id)
    VALUES ($1, $2);
    """
    for role in user.roles:
        role_id = await get_role_id(role)
        await db.execute(query, user_id, role_id)
    return { "message": "User successfully created" }


# Function to get the user from the database using the username
async def find_user_by_username(username: str) -> User:
    db = get_db()
    query = """
    SELECT
        u.user_id,
        u.username,
        u.email,
        u.password,
        u.disabled,
        array_agg(r.role_name) AS roles
    FROM
        users u
    JOIN
        user_roles ur ON u.user_id = ur.user_id
    JOIN
        roles r ON ur.role_id = r.role_id
    WHERE
        u.username = $1
    GROUP BY
        u.user_id, u.username, u.email;
    """
    result = await db.fetch_row(query, username)
    if result is None:
        return None
    user_dict = dict(result)
    user = User(
        username=user_dict["username"],
        email=user_dict["email"],
        name=user_dict["username"], 
        disabled=user_dict["disabled"], 
        password=user_dict["password"], 
        roles=user_dict["roles"]
        )
    return user


# Function to get the user from the database using the email
async def find_user_by_email(email: str) -> User:
    db = get_db()
    query = """
    SELECT
        u.user_id,
        u.username,
        u.email,
        u.password,
        u.disabled,
        array_agg(r.role_name) AS roles
    FROM
        users u
    JOIN
        user_roles ur ON u.user_id = ur.user_id
    JOIN
        roles r ON ur.role_id = r.role_id
    WHERE
        u.email = $1
    GROUP BY
        u.user_id, u.username, u.email;
    """
    result = await db.fetch_row(query, email)
    if result is None:
        return None
    user_dict = dict(result)
    user = User(
        username=user_dict["username"],
        email=user_dict["email"],
        name=user_dict["username"], 
        disabled=user_dict["disabled"], 
        password=user_dict["password"], 
        roles=user_dict["roles"]
        )
    return user


# Function to get a role id with its name
async def get_role_id(role_name: str) -> int:
    db = get_db()
    query = """
    SELECT role_id FROM roles WHERE role_name = $1;
    """
    role_id = await db.fetch_val(query, role_name)
    return role_id

# Function to get a user id with its username
async def get_user_id(username: str) -> UserIdAndUsername:
    db = get_db()
    query = """
    SELECT user_id FROM users WHERE username = $1;
    """
    user_id = await db.fetch_val(query, username)
    return UserIdAndUsername(user_id=user_id, username=username)


# Function to get all users
async def find_all_users() -> List[User]:
    db = get_db()
    query = """
    SELECT
        u.user_id,
        u.username,
        u.email,
        u.disabled,
        array_agg(r.role_name) AS roles
    FROM
        users u
    JOIN
        user_roles ur ON u.user_id = ur.user_id
    JOIN
        roles r ON ur.role_id = r.role_id
    GROUP BY
        u.user_id, u.username, u.email;
    """
    result = await db.fetch_rows(query)
    if result is None:
        return []
    users = []
    for row in result:
        user_dict = dict(row)
        user = User(
            username=user_dict["username"],
            email=user_dict["email"],
            name=user_dict["username"], 
            disabled=user_dict["disabled"], 
            password="Placeholder", 
            roles=user_dict["roles"]
            )
        users.append(user)
    return users

# Ban user by username
async def ban_user_by_username(username: str):
    db = get_db()
    query = """
    UPDATE users SET disabled = true WHERE username = $1;
    """
    await db.execute(query, username)
    return { "message": "User successfully banned" }