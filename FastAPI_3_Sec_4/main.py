from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List
import uuid

app = FastAPI()

# Allow frontend
origins = ["http://127.0.0.1:5500"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- Fake DB --------
users = {}   # email → {"username": ..., "password": ...}
sessions = {}  # token → email
posts = []    # list of posts

# -------- Models --------
class Post(BaseModel):
    id: str
    title: str
    content: str
    author: str
    comments: List[str] = []

# -------- Auth Helpers --------
def get_current_user(token: str):
    if token not in sessions:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return sessions[token]

# -------- Routes --------
@app.post("/signup")
def signup(username: str, email: str, password: str):
    if email in users:
        raise HTTPException(status_code=400, detail="Email already registered")
    users[email] = {"username": username, "password": password}
    return {"msg": "User registered"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = str(uuid.uuid4())
    sessions[token] = form_data.username
    return {"access_token": token, "token_type": "bearer"}

@app.get("/posts", response_model=List[Post])
def get_posts():
    return posts

@app.post("/posts", response_model=Post)
def create_post(title: str, content: str, token: str):
    email = get_current_user(token)
    post = Post(id=str(uuid.uuid4()), title=title, content=content, author=email, comments=[])
    posts.append(post)
    return post

@app.post("/posts/{post_id}/comments")
def add_comment(post_id: str, comment: str):
    for post in posts:
        if post.id == post_id:
            post.comments.append(comment)
            return {"msg": "Comment added", "post": post}
    raise HTTPException(status_code=404, detail="Post not found")
