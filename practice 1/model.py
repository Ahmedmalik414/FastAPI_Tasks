from pydantic import BaseModel, Field

class Task(BaseModel):
    id: int = Field(..., example=1)
    title: str = Field(..., example="Buy groceries")
    description: str = Field(..., example="Milk, eggs, and bread")
    completed: bool = Field(default=False, example=False)
