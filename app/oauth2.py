import os
from jose import JWTError, jwt
from datetime import timedelta, datetime
from fastapi import status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from . import schemas, database, models
from sqlalchemy.orm import Session



SECRET_KEY = os.environ.get('SECRET_KEY')
ALGORITHM = os.environ.get('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES'))


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')



def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt



def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # print('payload', payload)
        id: int = payload.get('user_id')

        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)  # validate token schema
        # print('token_data', token_data, 'type', type(token_data), token_data.id)
    
    except JWTError:
        raise credentials_exception
    
    return token_data




def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(database.get_db)):
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    
    token = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token.id).first()

    return user