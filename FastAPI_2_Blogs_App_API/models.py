from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, ForeignKey, Text

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)  
    email = Column(String(100), unique=True, index=True, nullable=False)  
    password = Column(String(200), nullable=False)                        
    role = Column(String(20), default="user")                             

    posts = relationship("Post", back_populates="user")
    comments = relationship("Comment", back_populates="user")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)      
    content = Column(String(5000), nullable=False)   
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(500), nullable=False) 
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))

    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")