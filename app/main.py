from fastapi import FastAPI, HTTPException, status, Response, Depends
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)


app = FastAPI()


my_posts = [{"title": "random", "content": "also random", "id": 1}, 
            {"title": "second", "content":"second stuff", "id": 2}]

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    id: int | None = None

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
def posts():
    cursor.execute("""SELECT * FROM posts """) #execute sql query
    posts = cursor.fetchall() #get all the results from database and store them in a variable
    return {"data": posts} #print the results

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.published))
    # We are inserting using a parameterized query method to prevent SQL injections. This way any input is never executed as a SQL query but treated as a string
    new_post = cursor.fetchone()
    #there are staged changes but we need to commit it to the database to finalize them. Very similar to github repos
    conn.commit()
    return {"updated_post": new_post}


@app.get("/posts/{id}")
def get_post(id: int): #anytime we have a path parameter, it will also be passed as a string so we need to parse it into an int for this to work
    cursor.execute("""SELECT * FROM posts WHERE id = %s""", (id,)) #we have to change it to tuple to let python know this is indexable (not super important) and tuples require a comma at the end if there is only one item
    post = cursor.fetchone()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    return {"post_detail": post}

@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"status": posts}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):

    cursor.execute("""DELETE FROM posts * WHERE id = %s RETURNING *""", (id,))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post == None: #if the deleted post was not found, then throw an error
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post (id: int, post: Post):
    
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", 
                    (post.title, post.content, post.published, id,))
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    return {"data": updated_post}