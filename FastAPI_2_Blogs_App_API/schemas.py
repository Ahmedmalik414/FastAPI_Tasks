from typing import List, Optional,Text
from pydantic import BaseModel,EmailStr,Field

#combined comment schema 
class CommentSchema(BaseModel):
    text: str
    post_id: int
    user_id :int

    class Config:
        from_attributes = True












#these are schemas only for request
class PostSchema(BaseModel):
    id: int =Field(...,description="id of post")
    title: str
    content: str
    comments: List[CommentSchema] = []

    class Config:
        from_attributes = True

class UserSchema(BaseModel):
    id: int
    username: str
    email: str
    posts: List[PostSchema] = []

    class Config:
        from_attributes = True
        














        
#response schemas         
        
        
class UserCreateSchema(BaseModel):
    username: str
    email: EmailStr
    password:Text
    
    
    class Config:
        from_attributes = True
        

class UserCreateSchema_response(BaseModel):
    username: str
    email: EmailStr
   
        
    
    class Config:
        from_attributes = True 
class PostCreateSchema(BaseModel):
    title: str
    content: str

    class Config:
        from_attributes = True
        


class LoginSchema(BaseModel):
    email: EmailStr
    password: str
    
    
    class Config:
        from_attributes = True
        
        
