from datetime import datetime

from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship

metadata = MetaData()

role = Table(
    "role",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False),
    Column("permissions", JSON),
)

user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String(100), nullable=False),
    Column("username", String(100), nullable=False),
    Column("registered_at", TIMESTAMP, default=datetime.utcnow),
    Column("role_id", Integer, ForeignKey(role.c.id)),
    Column("hashed_password", String(100), nullable=False),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_superuser", Boolean, default=False, nullable=False),
    Column("is_verified", Boolean, default=False, nullable=False),
)

post = Table(
    "posts",
    metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('title', String(100), index=True),
    Column('content', String(100), nullable=False),
    Column('author_id', Integer, ForeignKey('user.id')),
    Column('created_at', TIMESTAMP, nullable=False),
    Column('num_votes', Integer, default=0),  # Number of votes for the post
    Column('rating', Integer, default=0.0),      # Rating of the post
)

# Define the relationship between posts and users
posts = relationship("Post", back_populates="user")

vote = Table(
    "votes",
    metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('post_id', Integer, ForeignKey('posts.id')),
    Column('value', Integer),
)
