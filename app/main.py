from multiprocessing import synchronize
from fastapi import FastAPI, HTTPException, status, Response, Depends
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)


app = FastAPI()


my_posts = [{"title": "random", "content": "also random", "id": 1}, 
            {"title": "second", "content":"second stuff", "id": 2}]

while True:
    try:
        conn= psycopg2.connect(host='localhost', database='fastapi', user='postgres', 
        password='password', cursor_factory=RealDictCursor) #establish a connection to the database
        cursor = conn.cursor() #create a cursor object to execute SQL queries
        print("Database connection was succesful")
        break
        
    except Exception as error:
        print("Connecting to database failed")
        print("Error: ", error)
        time.sleep(2)

def find_post(id):
    for i in my_posts:
        if i['id'] == id:
            return i
        

def find_post_index(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i 

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/posts")
def posts(db: Session = Depends(get_db)):
    # Raw SQL query
    # cursor.execute("""SELECT * FROM posts """) #execute sql query
    # posts = cursor.fetchall() #get all the results from database and store them in a variable
    
    # SQLAlchemy query
    posts = db.query(models.Post).all()
    
    return posts

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: schemas.Post, db: Session = Depends(get_db)):
    
    # Raw SQL query
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.published))
    # # We are inserting using a parameterized query method to prevent SQL injections. This way any input is never executed as a SQL query but treated as a string
    # new_post = cursor.fetchone()
    # #there are staged changes but we need to commit it to the database to finalize them. Very similar to github repos
    # conn.commit()
    

    # SQLAlchemy query
    new_post = models.Post(**post.model_dump())
    # print(new_post)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    return new_post


@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)): #anytime we have a path parameter, it will also be passed as a string so we need to parse it into an int for this to work
    
    #Raw SQL query
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (id,)) #we have to change it to tuple to let python know this is indexable (not super important) and tuples require a comma at the end if there is only one item
    # post = cursor.fetchone()
    
    #SQLAlchemy query
    new_post = db.query(models.Post).filter(id == models.Post.id).first()
    
    if not new_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    
    
    return new_post

@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"status": posts}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    #Raw SQL query
    
    # cursor.execute("""DELETE FROM posts * WHERE id = %s RETURNING *""", (id,))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    
    #SQLAlchemy query
    deleted_post = db.query(models.Post).filter(id == models.Post.id) #start db instance and query db based on id
    print(deleted_post)
    if deleted_post.first() == None: #if the deleted post was not found, then throw an error
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")

    deleted_post.delete(synchronize_session=False) #delete() function removes the post found
    db.commit() # commit changes
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post (id: int, post: schemas.Post):
    
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", 
                    (post.title, post.content, post.published, id,))
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    return {"data": updated_post}