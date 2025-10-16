from database import Base
from sqlalchemy import Column,Integer,Float,String,DateTime,ForeignKey,Boolean
from datetime import datetime
class Transaction(Base):
    __tablename__= "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    amount = Column(Float)
    category = Column(String)
    description = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    important = Column(Boolean, default=False)
    
