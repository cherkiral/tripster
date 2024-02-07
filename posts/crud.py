from sqlalchemy import insert, select
from sqlalchemy.orm import Session
from datetime import datetime
from models import models
from sqlalchemy import func
from sqlalchemy import desc


async def create_post(db: Session, title: str, content: str, author_id: int):
    now = datetime.utcnow()
    query = insert(models.post).values(
        title=title,
        content=content,
        author_id=author_id,
        created_at=now,
        num_votes=0,  # Initialize num_votes with default value
        rating=0  # Initialize rating with default value
    )
    result = await db.execute(query)
    created_post_id = result.lastrowid
    await db.commit()
    return {'id': created_post_id, 'title': title, 'content': content, 'author_id': author_id, 'created_at': now,
            'num_votes': 0, 'rating': 0}


async def get_posts(db: Session, skip: int = 0, limit: int = 10):
    # Create a select statement for the 'posts' table
    stmt = select(models.post).offset(skip).limit(limit)

    # Execute the select statement and fetch the results
    result = await db.execute(stmt)

    # Fetch all rows from the result and return them
    posts = result.fetchall()
    return posts


# Function to get a vote by user and post
async def get_vote_by_user_and_post(db: Session, user_id: int, post_id: int):
    result = await db.execute(
        models.vote.select().where(models.vote.c.user_id == user_id, models.vote.c.post_id == post_id))
    return result.fetchone()


async def calculate_post_rating(db: Session, post_id: int):
    # Query to calculate the sum of vote values for a given post
    result = await db.execute(select(func.sum(models.vote.c.value), func.count(models.vote.c.id)).where(models.vote.c.post_id == post_id))
    total_votes, num_votes = result.fetchone()

    # Update the post's rating and number of votes
    update_query = (
        models.post.update()
        .where(models.post.c.id == post_id)
        .values(rating=total_votes, num_votes=num_votes)
    )
    await db.execute(update_query)
    await db.commit()



async def create_vote(db: Session, user_id: int, post_id: int, vote_value: int):
    new_vote = models.vote.insert().values(user_id=user_id, post_id=post_id, value=vote_value)
    await db.execute(new_vote)
    await db.commit()
    await calculate_post_rating(db, post_id)


async def update_vote_value(db: Session, vote_id: int, vote_value: int):
    update_query = models.vote.update().where(models.vote.c.id == vote_id).values(value=vote_value)
    await db.execute(update_query)
    await db.commit()
    # Fetch post ID associated with the vote
    result = await db.execute(select(models.vote.c.post_id).where(models.vote.c.id == vote_id))
    post_id = result.scalar()
    await calculate_post_rating(db, post_id)

async def delete_vote_by_user_and_post(db: Session, user_id: int, post_id: int):
    # Query to delete the vote by user ID and post ID
    query = models.vote.delete().where(
        (models.vote.c.user_id == user_id) & (models.vote.c.post_id == post_id)
    )
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0  # Return True if at least one row was deleted


async def get_top_rated_posts(db: Session, limit: int = 10):
    # Create a select statement for the 'posts' table
    stmt = select(models.post).order_by(models.post.c.rating.desc()).limit(limit)

    # Execute the select statement and fetch the results
    result = await db.execute(stmt)

    # Fetch all rows from the result and convert them to dictionaries
    top_rated_posts = [dict(row) for row in result.mappings().fetchall()]

    return top_rated_posts
