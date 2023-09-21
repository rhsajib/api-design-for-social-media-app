from fastapi import status, HTTPException, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import models, schemas, database, utils, oauth2


router = APIRouter(tags= ['Authentication'])


@router.post('/login', response_model=schemas.Token)
# def login(user_credentials: schemas.UserLogin, db: Session = Depends(database.get_db)):
#     user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(database.get_db)):

    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invalid Credentials')
    
    if not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invalid Credentials')
    
    # create a token
    access_token = oauth2.create_access_token(data={'user_id': user.id})

    # decode access token using the following url
    # https://jwt.io/

    # return a token
    return {'access_token': access_token, 'token_type': 'bearer'}