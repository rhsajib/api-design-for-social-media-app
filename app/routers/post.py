from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, database, oauth2




router = APIRouter(
    prefix='/posts',
    tags= ['Posts']         # group the posts in Posts catagory in 127.0.0.1:8000/docs
)




# read all post
@router.get('/', response_model=list[schemas.Post])
def get_posts(db: Session = Depends(database.get_db),
              current_user: int = Depends(oauth2.get_current_user),
              limit: int = 10):
    posts = db.query(models.Post).limit(limit).all()

    # get all posts of a specific user id
    # posts = db.query(models.Post).filter(models.Post.user_id == current_user.id).all()

    return posts


# read single post
@router.get('/{id}', response_model=schemas.Post)
def get_post_detail(id: int, 
                    db: Session = Depends(database.get_db),
                    current_user: int = Depends(oauth2.get_current_user)):
    
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id: {id} was not found')
    return post


# create post
@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, 
                db: Session = Depends(database.get_db),
                current_user: int = Depends(oauth2.get_current_user)):

    # new_post = models.Post(title=post.title, content=post.content, published=post.published)
    new_post = models.Post(user_id = current_user.id, **post.model_dump())
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


# update post  
@router.put('/{id}', response_model=schemas.Post)
def create_post(id: int, 
                updated_post: schemas.PostUpdate,  
                db: Session = Depends(database.get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id: {id} does not exist!')
    
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Not authorized to perform requested action!')
   
    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()

    return post


# delete post
@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, 
                db: Session = Depends(database.get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id: {id} does not exist!')
    
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Not authorized to perform requested action!')
    
    post_query.delete(synchronize_session=False)
    db.commit()
    return {'message': 'post deleted'}







