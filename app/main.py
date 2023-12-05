from fastapi import FastAPI, Cookie, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from jose import jwt 
from fastapi.security import OAuth2PasswordBearer
import json
from pydantic import BaseModel
from sqlalchemy.orm import Session
from users_repository import UserCreate, UserCreateRequest, UsersRepository, UserLogin, UserEdit
from announcements_repository import AnnounceCreateRequest, AnnouncementsRepository, AnnounceCreate, AnnounceEdit, AnnounceResponse
from comments_repository import CommentCreateRequest, CommentCreate, CommentsRepository
from favorites_repository import FavoritesRepository
from database import SessionLocal

users_repo = UsersRepository()
announce_repo = AnnouncementsRepository()
comments_repo = CommentsRepository()
favs_repo = FavoritesRepository()

app = FastAPI()
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
oath2_scheme = OAuth2PasswordBearer(tokenUrl = 'token')
#jwt
def create_jwt(user_id: int):
    data = {'user_id': user_id}
    token = jwt.encode(data, 'Super-Secret', 'HS256')
    return token
def decode_jwt(token):
    data = jwt.decode(token,'Super-Secret', 'HS256')
    return data['user_id']
    
#signup
@app.post('/signup')
def signup(user: UserCreateRequest, db: Session=Depends(get_db)):
    users_repo.save(user, db)
    return {'msg': 'successully registered!'}
    
#login
@app.post('/token')
def login(username:str=Form(), password:str=Form(), db: Session = Depends(get_db)):
    if users_repo.get_by_username(db, username) is None:
        raise HTTPException(status_code = 404, detail='User NotFound')
    else: 
        user = users_repo.get_by_username(db, username)
    if user.password!=password:
        raise HTTPException(status_code=403, detail='Forbidden')
    token = create_jwt(user.id)
    return {'access_token': token}
        
#profile
@app.get('/auth/users/me')
def get_profile(db:Session=Depends(get_db),token: str = Depends(oath2_scheme)):
    user_id = decode_jwt(token)
    user = users_repo.get_by_id(db,user_id)
    return user
         
@app.patch('/auth/users/me')
def edit_user(input: UserEdit, token: str = Depends(oath2_scheme), db: Session=Depends(get_db)):
    user_id = decode_jwt(token)
    user = users_repo.get_by_id(db, user_id)
    users_repo.update(db, user_id, UserCreate(input.username, input.password, input.phone, input.name, input.city))
    return {'msg':'successfully edited!'}
    
    
@app.post('/shanyraks')
def post_announcements(input: AnnounceCreateRequest, token: str=Depends(oath2_scheme),db:Session=Depends(get_db)):
    user_id = decode_jwt(token)
    announcement = AnnounceCreate(input.type_, input.price, input.address, input.area, input.rooms_count, input.description)
    announce_repo.create(db, user_id, announcement)
    return {'id': 'to change' }
    
#announcements  get
@app.get('/shanyraks')
def get_announcements(db:Session=Depends(get_db)):
    shanyraks = announce_repo.get_all(db)
    return shanyraks
    
#announcements  patch
@app.patch('/shanyraks/{id}')
def edit_announcements(id: int, input: AnnounceEdit, token: str = Depends(oath2_scheme), db:Session=Depends(get_db)):
    user_id = decode_jwt(token)
    user = users_repo.get_by_id(db, user_id)
    shanyrak = announce_repo.get_by_id(db,id)
    if user.id!=shanyrak.user_id:
        raise HTTPException(status_code=403, detail='Forbidden')
    announce_repo.update(db, AnnounceCreate(input.type_, input.price, input.address, input.area, input.rooms_count, input.description), id )
    return {'msg': 'successfully edited'}
    
@app.delete('/shanyraks/{id}')
def delete(id: int, token: str = Depends(oath2_scheme), db:Session=Depends(get_db)):
    user_id = decode_jwt(token)
    user = users_repo.get_by_id(db, user_id)
    shanyrak = announce_repo.get_by_id(db, id)
    if user.id!=shanyrak.user_id:
        raise HTTPException(status_code=403, detail='Forbidden')
    announce_repo.delete_(db, id)
    return {'msg':'deleted'}
    
@app.post('/shanyraks/{id}/comments')
def comments(id: int, input: CommentCreateRequest, token: str=Depends(oath2_scheme), db:Session=Depends(get_db)):
    comment = CommentCreate(content = input.content)
    user_id = decode_jwt(token)
    if users_repo.get_by_id(db, user_id) is None:
        raise HTTPException(status_code=404, detail="UserNotFound")
    else:
        user = users_repo.get_by_id(db, user_id)
    comments_repo.save(db,comment,user.id,id)
    shanyrak = announce_repo.get_by_id(db, id)
    announce_repo.increase_comments(db, id)
    return {'msg': 'comment was added'}

@app.get('/shanyraks/{id}/comments')
def get_comments(id,db:Session=Depends(get_db)):
    users = comments_repo.get_all_by_id(db, id)
    return users

@app.patch('/shanyraks/{id}/comments/{comment_id}')
def patching(id: int, comment_id: int, input: CommentCreateRequest,db:Session=Depends(get_db), token: str=Depends(oath2_scheme)):
    user_id = decode_jwt(token)
    user = users_repo.get_by_id(db,user_id)
    shanyrak = announce_repo.get_by_id(db, id)
    if shanyrak is None:
        raise HTTPException(status_code=404, detail="Shanyrak Not Found")
    if shanyrak.user_id!=user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    comments_repo.update(db, comment_id, input)
    return {'msg':'edited'}
    
@app.delete('/shanyraks/{id}/comments/{comment_id}')
def delete(id: int, comment_id: int, db:Session=Depends(get_db), token: str=Depends(oath2_scheme)):
    user_id = decode_jwt(token)
    user = users_repo.get_by_id(db, user_id)
    comment = comments_repo.get_by_id(db, id)
    if user.id!=comment.user_id:
        raise HTTPException(status_code=403, detail='Forbidden')
    comments_repo.delete(db, comment_id)
    announce_repo.decrease_comments(db, id)
    return {'msg': 'deleted'}
       
@app.get('/shanyraks/{id}')
def get_comments(id: int, db:Session=Depends(get_db)):
    shanyrak = announce_repo.get_by_id(db, id)
    return shanyrak

@app.post('/auth/users/favorites/shanyraks/{id}')
def add_to_favs(id: int, db:Session=Depends(get_db), token: str=Depends(oath2_scheme)):
    user_id = decode_jwt(token)
    shanyrak = announce_repo.get_by_id(db, id)
    if shanyrak:
        favs_repo.save(db, user_id, id)
        return {'msg': 'saved to favorites'}
    else: 
        raise HTTPException(detail='shanyrak Not Found', status_code=404)
@app.get('/auth/users/favorites/shanyraks')
def get_favs(db:Session=Depends(get_db), token: str=Depends(oath2_scheme)):
    user_id = decode_jwt(token)
    favs = favs_repo.get_all_by_id(db, user_id)
    return favs
@app.delete('/auth/users/favorites/shanyraks/{id}')
def del_favs(id: int, db:Session=Depends(get_db), token:str=Depends(oath2_scheme)):
    fav = favs_repo.get_by_id(db,id)
    if fav:
        favs_repo.delete(db, id)
    else:
        raise HTTPException(detail='Not Found', status_code=404)
    return {'deleted from favs'}
@app.get('/search')
def search(limit: int, offset:int, type: str=None, rooms_count: int=None,price_from: int=None, price_until: int=None, db:Session=Depends(get_db)):
    shanyraks = announce_repo.filter_search(db,limit, offset, type, rooms_count,price_from, price_until)
    return {'total': len(shanyraks), 'objects': shanyraks}
    