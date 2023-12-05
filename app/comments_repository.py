from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, Session
from database import Base
from pydantic import BaseModel
from attrs import define

class CommentCreateRequest(BaseModel):
    content: str
    
@define   
class CommentCreate:
    content: str
    
class Comment(Base):
    __tablename__ = 'comment'
    id=Column(Integer,primary_key=True)
    content=Column(String)
    post_id = Column(Integer, ForeignKey('announcement.id'))
    user_id=Column(Integer,ForeignKey('user.id'))
    user = relationship('User', back_populates='comment')
    announcement = relationship('Announcement', back_populates='comment')
class CommentEdit(BaseModel):
    content: str
class CommentsRepository:
    def save(self, db:Session, input, user_id, post_id):
        comment = Comment(content=input.content, post_id = post_id, user_id=user_id)
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment
    def get_all_by_id(self, db:Session, id:int,skip: int=0, limit: int=10):
        return db.query(Comment).filter(id==Comment.post_id).offset(skip).limit(limit).all()
    def get_by_id(self, db:Session, id:int):
        return db.query(Comment).filter(id==Comment.id).first()
    def update(self, db:Session,comment_id, input):
        comment = db.query(Comment).filter(Comment.id==comment_id).first()
        if comment:
            comment.content = input.content
            db.commit()
            db.refresh(comment)
    def delete(self, db:Session, comment_id):
        to_delete = db.query(Comment).filter(comment_id==Comment.id).first()
        db.delete(to_delete)
        db.commit()
    