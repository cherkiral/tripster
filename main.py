from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from fastapi_users import fastapi_users, FastAPIUsers
from pydantic import BaseModel, Field

from fastapi import FastAPI, Request, status, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
# from fastapi.exceptions import ValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import select

from auth.auth import auth_backend
from auth.database import User
from auth.manager import get_user_manager
from auth.schemas import UserRead, UserCreate
from posts import crud
from posts.crud import create_post, get_posts
from posts.schemas import PostCreate, PostRead
from auth.database import get_async_session
from sqlalchemy.orm import Session

app = FastAPI(
    title="Trading App"
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

current_user = fastapi_users.current_user()


async def current_user_id(user: User = Depends(current_user)):
    return user.id


@app.get("/protected-route")
def protected_route(user: User = Depends(current_user)):
    return f"Hello, {user.username}"


@app.get("/unprotected-route")
def unprotected_route():
    return f"Hello, anonym"


@app.post("/posts/", response_model=PostRead)
async def create_post_route(
    post: PostCreate,
    db: Session = Depends(get_async_session),
    user_id: int = Depends(current_user_id)
):
    created_post = await create_post(db, title=post.title, content=post.content, author_id=user_id)
    return created_post


@app.get("/posts/", response_model=List[PostRead])
async def get_posts_route(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_async_session)
):
    posts = await get_posts(db, skip=skip, limit=limit)  # Await the execution of get_posts
    return posts


@app.post("/posts/{post_id}/vote/")
async def vote_for_post(post_id: int, vote_value: int, user_id: int = Depends(current_user_id), db: Session = Depends(get_async_session)):
    # Check if the user has already voted for the post
    existing_vote = await crud.get_vote_by_user_and_post(db, user_id=user_id, post_id=post_id)

    if existing_vote:
        # If the user has already voted, update the vote value
        await crud.update_vote_value(db, vote_id=existing_vote.id, vote_value=vote_value)
    else:
        # If the user has not voted yet, insert a new vote
        await crud.create_vote(db, user_id=user_id, post_id=post_id, vote_value=vote_value)

    return {"message": "Vote recorded successfully"}


@app.delete("/votes/")
async def delete_vote(post_id: int, db: Session = Depends(get_async_session), user_id: int = Depends(current_user_id)):
    # Check if the user has already voted for the post
    existing_vote = await crud.get_vote_by_user_and_post(db, user_id=user_id, post_id=post_id)

    if not existing_vote:
        raise HTTPException(status_code=404, detail="Vote not found")

    # Check if the vote belongs to the authenticated user
    if existing_vote.user_id != user_id:
        raise HTTPException(status_code=403, detail="You are not authorized to delete this vote")

    # Delete the vote by user ID and post ID
    vote_deleted = await crud.delete_vote_by_user_and_post(db, user_id, post_id)
    if vote_deleted:
        return {"message": "Vote deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete vote")

@app.get("/top-rated-posts/")
async def get_top_rated_posts_route(db: Session = Depends(get_async_session)):
    top_rated_posts = await crud.get_top_rated_posts(db)
    return top_rated_posts
