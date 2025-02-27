from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel
from random import randrange

app = FastAPI()

my_posts = [{"title": "random", "content": "also random", "id": 1}, {"title": "second", 
                                                                     "content":"second stuff", "id": 2}]

class Post(BaseModel):
    title: str
    content: str
    rating: int | None = None
    id: int | None = None

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
    return {"data": my_posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    post_dict = post.model_dump() #creating dict using pydantic function
    post_dict['id'] = randrange(0, 10000000) #assign a random unique value to the id field found in post BaseModel
    my_posts.append(post_dict) #update the local array to include the dictionary created from our POST request
    return {"updated_post": post_dict} #return the dictionary as a response of a successful POST request


@app.get("/posts/{id}")
def get_post(id: int): #anytime we have a path parameter, it will also be passed as a string so we need to parse it into an int for this to work
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    return {"post_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    index = find_post_index(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)