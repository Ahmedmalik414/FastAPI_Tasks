from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column,String,Integer,ForeignKey,Text


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password= Column(Text)

    # Relationship 
    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")



class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    

    # Relationships
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
   



class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))

    # Relationship
    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")



