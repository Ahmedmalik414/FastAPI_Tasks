from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from schemas import UserSchema,UserCreateSchema,PostSchema,CommentSchema,PostCreateSchema,UserCreateSchema_response,LoginSchema
import models
import uvicorn
from utils import get_database,hash_pwd,verify_hashed_pwd,create_refresh_token,create_access_token

app = FastAPI(title="My Blogs App")
from datetime import datetime, timedelta
from jose import JWTError, jwt







#get particular users data 
@app.get("/user/{user_id}", response_model=UserSchema)
def get_user(user_id: int, db: Session = Depends(get_database)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


#create a new user
@app.post("/create_account",response_model=UserCreateSchema_response)
def create_user(user: UserCreateSchema, db: Session = Depends(get_database)):
    new_user = models.User(
        username=user.username,
        email=user.email,
        password = hash_pwd(user.password)
        )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
   
   
   
#create a new post for a particular user     
@app.post("/create_post/{user_id}")
def create_post(user_id:int,post:PostCreateSchema,db: Session = Depends(get_database)):
    new_post=models.Post(
         title= post.title,
         content= post.content,
         user_id = user_id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post
from fastapi import Body



#update a post using this 
@app.patch("/update_post/{post_id}", response_model=PostCreateSchema)
def update_post(post_id: int, post: PostCreateSchema, db: Session = Depends(get_database)):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.title:
        db_post.title = post.title
    if post.content:
        db_post.content = post.content

    db.commit()
    db.refresh(db_post)
    return db_post


#delete any post using its id
@app.delete("/delete_post/{user_id}/{post_id}", status_code=200)
def delete_post(user_id: int, post_id: int, db: Session = Depends(get_database)):
    db_post = db.query(models.Post).filter(
        models.Post.id == post_id,
        models.Post.user_id == user_id
    ).first()
    
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found or not owned by user")
    
    db.delete(db_post)
    db.commit()
    return {"detail": "Post deleted successfully"}


#create a comment on a post using user id and post id  
@app.post("/create_comment/{user_id}/{post_id}")
def create_comment(user_id:int,post_id:int,comment:CommentSchema,db: Session = Depends(get_database)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    post= db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    new_comment=models.Comment(
        
         text = comment.text,
         post_id = post_id,
         user_id=user_id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


#update any comment
@app.patch("/update_comment/{comment_id}", response_model=CommentSchema)
def update_comment(comment_id: int, comment: CommentSchema, db: Session = Depends(get_database)):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment.text:
        db_comment.text = comment.text
    
    db.commit()
    db.refresh(db_comment)
    return db_comment


#delete any comment
@app.delete("/delete_comment/{user_id}/{comment_id}", status_code=200)
def delete_comment(user_id: int, comment_id: int, db: Session = Depends(get_database)):
    db_comment = db.query(models.Comment).filter(
        models.Comment.id == comment_id,
        models.Comment.user_id == user_id
    ).first()
    
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found or not owned by user")
    
    db.delete(db_comment)
    db.commit()
    return {"detail": "Comment deleted successfully"}

          
          
                
@app.get("/posts/{user_id}")
def get_user_posts(user_id: int, db: Session = Depends(get_database)):
    posts = db.query(models.Post).filter(models.Post.user_id == user_id).all()
    if not posts:
        raise HTTPException(status_code=404, detail="No posts found for this user")
    return posts




@app.get("/posts/{post_id}/comments")
def get_post_comments(post_id: int, db: Session = Depends(get_database)):
    comments = db.query(models.Comment).filter(models.Comment.post_id == post_id).all()
    return comments    

from fastapi import Body

from fastapi.responses import JSONResponse

@app.post("/login")
def login_user(credentials: LoginSchema, db: Session = Depends(get_database)):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    if not verify_hashed_pwd(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})

    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,   
        secure=True,    
        samesite="Lax"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="Lax"
    )

    return response

    
    



    
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
    
    
    

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8008, reload=True)
