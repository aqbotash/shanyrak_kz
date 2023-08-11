from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, Session
from database import Base
from pydantic import BaseModel
from attrs import define
    
class Favorite(Base):
    __tablename__ = 'favorite'
    id=Column(Integer,primary_key=True)
    post_id = Column(Integer, ForeignKey('announcement.id'))
    user_id=Column(Integer,ForeignKey('user.id'))
    user = relationship('User', back_populates='fav')
    announcement = relationship('Announcement', back_populates='fav')
    
class FavoritesRepository:
    def save(self, db:Session, user_id, post_id):
        fav = Favorite(post_id = post_id, user_id=user_id)
        db.add(fav)
        db.commit()
        db.refresh(fav)
        return fav
    def get_all_by_id(self, db:Session, id:int,skip: int=0, limit: int=10):
        return db.query(Favorite).filter(id==Favorite.user_id).offset(skip).limit(limit).all()
    def get_by_id(self, db:Session, id:int):
        return db.query(Favorite).filter(id==Favorite.user_id).first()
    def delete(self, db:Session, fav_id):
        to_delete = db.query(Favorite).filter(fav_id==Favorite.id).first()
        db.delete(to_delete)
        db.commit()