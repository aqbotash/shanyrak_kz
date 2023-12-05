from sqlalchemy import Column, Integer, String, Float, ForeignKey, update, and_
from sqlalchemy.orm import relationship, Session
from database import Base
from pydantic import BaseModel
from attrs import define

class AnnounceCreateRequest(BaseModel):
    type_: str
    price: int
    address: str
    area: float
    rooms_count: int
    description: str

@define
class AnnounceCreate:
    type_: str
    price: int
    address: str
    area: float
    rooms_count: int
    description: str

class AnnounceEdit(BaseModel):
    type_: str
    price: int
    address: str
    area: float
    rooms_count: int
    description: str
    
class AnnounceResponse(BaseModel):
    type_: str
    price: int
    address: str
    area: float
    rooms_count: int
    description: str
    user_id: int
    total_comments: int=0
    
class Announcement(Base):
    __tablename__ = 'announcement'
    
    id = Column(Integer, primary_key=True, index=True)
    type_ = Column(String)
    price = Column(Integer)
    address = Column(String)
    area = Column(Float)
    rooms_count = Column(Integer)
    description = Column(String)
    total_comments = Column(Integer, default=0)
    user_id=Column(Integer,ForeignKey('user.id'))
    user = relationship('User', back_populates='announcement')
    comment = relationship('Comment', back_populates='announcement')
    fav = relationship('Favorite', back_populates='announcement')
    
    
class AnnouncementsRepository:
    def get_all(self, db: Session, skip: int=0, limit: int=10):
        return db.query(Announcement).offset(skip).limit(limit).all()
    def create(self, db: Session, user_id, input: AnnounceCreateRequest):
        announcement = Announcement(type_ = input.type_, price = input.price, address = input.address, area = input.area, rooms_count = input.rooms_count, description = input.description, user_id = user_id)
        db.add(announcement)
        db.commit()
        db.refresh(announcement)
    def get_by_id(self, db: Session, id: int):
        return db.query(Announcement).filter(id==Announcement.id).first()
    def update(self, db:Session, input: AnnounceEdit, id: int):
        current = db.query(Announcement).filter(id==Announcement.id).first()
        if current:
            current.type_ = input.type_
            current.price = input.price
            current.address = input.address
            current.area = input.area
            current.rooms_count = input.rooms_count
            current.description = input.description
            db.commit()
            db.refresh(current)
        return current
    def delete_(self, db:Session, id: int):
        to_delete = db.query(Announcement).filter(id==Announcement.id).first()
        if to_delete:
            db.delete(to_delete)
            db.commit()
    def increase_comments(self, db:Session, id):
        shanyrak = db.query(Announcement).filter(id==Announcement.id).first()
        shanyrak = update(Announcement).where(Announcement.id == id).values(total_comments=Announcement.total_comments + 1)
        db.execute(shanyrak)
        db.commit()
    def decrease_comments(self, db:Session,id):
        shanyrak = db.query(Announcement).filter(id==Announcement.id).first()
        if  shanyrak.total_comments>0:
            shanyrak = update(Announcement).where(Announcement.id==id).values(total_comments=Announcement.total_comments-1)
            db.execute(shanyrak)
            db.commit()
    def filter_search(self,db:Session,limit: int, offset:int, type_: str=None, rooms_count: int=None,price_from: int=None, price_until: int=None):
        conditions = []
        if rooms_count:
            conditions.append(Announcement.rooms_count==rooms_count)
        if price_from:
            conditions.append(Announcement.price >= price_from)
        if price_until:
            conditions.append(Announcement.price <= price_until)
        if type_:
            conditions.append(Announcement.type_ == type_)
        shanyraks = db.query(Announcement).filter(and_(*conditions)).offset(offset).limit(limit).all()
        return shanyraks
        
            
            
        
        
        
        
        
        
        
        
        
    