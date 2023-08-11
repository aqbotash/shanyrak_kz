from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, Session
from database import Base
from pydantic import BaseModel
from attrs import define

class UserCreateRequest(BaseModel):
    username: str
    phone: int
    password: str
    name: str
    city: str
    
@define
class UserCreate:
    username: str
    phone: int
    password: str
    name: str
    city: str
    
class UserLogin(BaseModel):
    username: str
    password: str

        
class UserEdit(BaseModel):
    username: str
    phone: int
    password: str
    name: str
    city: str

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    phone = Column(Integer)
    password = Column(String)
    name = Column(String)
    city = Column(String)
    comment = relationship('Comment', back_populates='user')
    announcement = relationship('Announcement', back_populates='user')
    fav = relationship('Favorite', back_populates='user')
   
class UsersRepository:
    def save(self, user: UserCreate, db: Session):
        new_user = User(**user.model_dump())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    def get_by_username(self, db:Session, username):
        return db.query(User).filter(username==User.username).first()
    def get_by_id(self, db:Session, user_id):
        return db.query(User).filter(user_id==User.id).first()
    def get_all(self, db: Session, skip: int=0, limit: int=10):
        return db.query(User).offset(skip).limit(limit)
    def update(self, db: Session, user_id, input):
        current = db.query(User).filter(user_id==User.id).first()
        if current:
            current.username=input.username
            current.password=input.password
            current.phone = input.phone 
            current.name = input.name
            current.city = input.city
            db.commit()
            db.refresh(current)
        return current