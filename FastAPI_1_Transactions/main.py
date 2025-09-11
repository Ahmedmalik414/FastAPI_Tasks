from typing import List, Optional,Required
from fastapi import FastAPI, Depends,HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal,engine,Base
from models import Transaction
from pydantic import BaseModel,Field
app = FastAPI(title="Personal Finance Tracker")

class TransactionSchema(BaseModel):
    id: Optional[int]= Field(description="Transaction id")
    user_id: int= Field(...,gt=0,description="user id")
    amount: float= Field(...,gt=0,description="Transaction of how much amount")
    category: str= Field(...,description="category of transaction")
    description: Optional[str]
    important: Optional[bool] = False
class UpdateTransactionSchema(BaseModel):
    id: int
    user_id: Optional[int]
    amount: Optional[float]=Field(gt=0,description="Transaction of how much amount")
    category: Optional[str]
    description: Optional[str]
    important: Optional[bool] = False    

    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

          
@app.get("/")
def home():
    return "Hello welcome"


@app.get("/transactions", response_model=List[TransactionSchema])
def get_transactions(db: Session = Depends(get_db)):
    transactions = db.query(Transaction).all()
    if not transactions:
        raise HTTPException(status_code=404, detail="No transaction foud")
    return transactions
  
        


@app.post("/transactions", response_model=TransactionSchema,status_code=201)
def create_transaction(transaction: TransactionSchema, db: Session = Depends(get_db)):
    db_transaction = Transaction(
        user_id=transaction.user_id,
        amount=transaction.amount,
        category=transaction.category,
        description=transaction.description,
        important=transaction.important
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)  
    return db_transaction


@app.delete("/delete_transection/{transaction_id}",status_code=204)
def delete_transactions(transaction_id: int, db: Session = Depends(get_db)):
   transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
   if not transaction:
       raise HTTPException(status_code=404,detail="Transaction not found")
   db.delete(transaction)
   db.commit()

@app.patch("/update_transaction/{transaction_id}",status_code=200)
def update_transaction(transaction_id : int ,update: UpdateTransactionSchema,db:Session=Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404,detail="Transaction not found")        
    if update.amount is not None:
        transaction.amount = update.amount
    if update.category is not None:
        transaction.category = update.category
    if update.description is not None:
        transaction.description = update.description
    if update.important is not None:
        transaction.important = update.important
    db.commit()
    db.refresh(transaction)
    return transaction
        
    
    
if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)  # synchronous, safe here
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
