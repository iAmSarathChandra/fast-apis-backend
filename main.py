from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from database import StoryResponse, DefaultStory, BannerResponse , Banner, MetadataResponse,GenreResponse,Genre
from database import SubGenreResponse,SubGenre, UserResponse , User, Keyword
import openai
import os
from typing import Dict, Optional
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from starlette.requests import Request
import random
from typing import List
import random
from sqlalchemy.orm import Session

app = FastAPI()


app.mount("/styles", StaticFiles(directory="styles"), name="styles")
templates = Jinja2Templates(directory="templates")

# Define the path to the templates directory
templates_dir = Path("templates")
index_file = templates_dir / "index.html"


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Other routes for the pages (Create, Read, Upload) can be done similarly
@app.get("/create", response_class=HTMLResponse)
async def create_page(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})

@app.get("/read", response_class=HTMLResponse)
async def read_page(request: Request):
    return templates.TemplateResponse("read.html", {"request": request})

@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.get("/banners", response_model=list[BannerResponse])
async def get_banners(db: Session = Depends(get_db)):
    try:
        # Query for banners
        banners = db.query(Banner).all()
        if not banners:
            raise HTTPException(status_code=404, detail="No banners found")
        return banners
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No story in data base {str(e)}")
    
    
@app.get("/stories", response_model=StoryResponse)
async def get_story(story_id: int, db: Session = Depends(get_db)):
    print("before try")
    try:
        print("Try case")
        # Fetch the story based on the ID
        story = db.query(DefaultStory).filter(DefaultStory.id == story_id).first()
        if not story:
            raise HTTPException(status_code=404, detail="Story not found")
        return story
    except Exception as e:
        print("Exception case")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    
@app.get("/stories/genre", response_model=list[StoryResponse])
async def get_story_by_genre(genre: str, db: Session = Depends(get_db)):
    print("before try")
    try:
        print("Try case")
        # Fetch the story based on the ID
        story = db.query(DefaultStory).filter(DefaultStory.genre == genre)
        if not story:
            raise HTTPException(status_code=404, detail="Story not found")
        return story
    except Exception as e:
        print("Exception case")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    
@app.get("/metadata/genre", response_model=list[MetadataResponse])
async def get_metadata_by_genre(genre: str, db: Session = Depends(get_db)):
    print("before try")
    try:
        print("Try case")
        # Fetch the story based on the ID
        story = db.query(DefaultStory).filter(DefaultStory.genre == genre)
        if not story:
            raise HTTPException(status_code=404, detail="Story not found")
        return story
    except Exception as e:
        print("Exception case")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/genres", response_model=list[GenreResponse])
def get_all_genres(db: Session = Depends(get_db)):
    try:
        genres = db.query(Genre).all()  # Query all genres from the tblgenres table
        if not genres:
            raise HTTPException(status_code=404, detail="No genres found")
        return genres
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    
@app.get("/subgenres", response_model=list[SubGenreResponse])
def get_subgenres_by_genre(genre_id: int, db: Session = Depends(get_db)):
    try:
        # Query subgenres where genre_id matches
        subgenres = db.query(SubGenre).filter(SubGenre.genre_id == genre_id).all()
        if not subgenres:
            raise HTTPException(status_code=404, detail="No subgenres found for the given genre ID")
        return subgenres
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
# Helper function to get 5 random keywords for a given subgenre_id
def get_random_keywords(subgenre_id: int, db: Session):
    try:
        # Query to fetch keywords based on subgenre_id
        keywords = db.query(Keyword).filter(Keyword.subgenre_id == subgenre_id).all()

        if not keywords:
            raise HTTPException(status_code=404, detail="No keywords found for the provided subgenre_id")

        # If there are fewer than 5 keywords, return all of them
        if len(keywords) < 5:
            return [keyword.name for keyword in keywords]

        # Randomly select 5 keywords
        random_keywords = random.sample([keyword.name for keyword in keywords], 5)
        return random_keywords

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Route to fetch random keywords for a given subgenre_id
@app.get("/keywords/{subgenre_id}", response_model=List[str])
def fetch_keywords(subgenre_id: int, db: Session = Depends(get_db)):
    try:
        keywords = get_random_keywords(subgenre_id, db)
        return keywords
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


    
@app.get("/userinfo", response_model=UserResponse)
def get_user_info(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

'''OPEN AI INTEGRATION'''

story_store: Dict[str, dict[str, Optional[str]]] = {}



# Request body model
class StoryRequest(BaseModel):
    prompt: str
    word_count: int

# Dummy data store (similar to story_store in the original code)
story_store: Dict[str, dict] = {}


@app.post("/generate-story")
async def generate_story(request: StoryRequest):
    request_id = str(len(story_store) + 1)
    
    # Hardcoded dummy story parts for testing
    dummy_story_part_1 = "Amelia and Grace met under the moonlit sky, their hearts racing with desire. They had been friends for years, but tonight they allowed themselves to explore a new level of intimacy. As they undressed each other, their hands caressed every inch of skin, igniting a fire between them. Grace traced her fingers along Amelia's curves, sending shivers down her spine. They moved together in a dance of passion, exploring each other's bodies in the darkness of the night. With each kiss and touch, they felt a connection deepening between them, a love that had been waiting to be unleashed. And as they gave themselves fully to each other, they knew that this was just the beginning of a love story worth telling."
    dummy_story_part_2 = "The knight faced many challenges along the way, including dragons, enchanted forests, and mysterious beings."

    # Store the request in the dummy store
    story_store[request_id] = {
        "prompt": request.prompt,
        "word_count": request.word_count,
        "generated_parts": [dummy_story_part_1, dummy_story_part_2]
    }

    # Return the hardcoded response
    return {"request_id": request_id, "first_part": dummy_story_part_1}


@app.post("/generate-story-comment")
async def generate_story(request: StoryRequest):
    request_id = str(len(story_store) + 1)
    
    # Initiate story generation
    story_store[request_id] = {"prompt": request.prompt, "word_count": request.word_count, "generated_parts": []}
    
    # Call OpenAI API to generate the first half of the story
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f"Write a story based on the prompt: '{request.prompt}' with around {request.word_count} words. Start with the first part."}
            ]
        )
        # Save the first part of the story in the store and include it in the response
        story_part = response["choices"][0]["message"]["content"]
        story_store[request_id]["generated_parts"].append(story_part)
        print("Story is : " +story_part   + "REQUEST ID : " + request_id)
        return {"request_id": request_id, "first_part": story_part}
    except Exception as e:
        # Handle API errors
        story_store.pop(request_id, None)  # Cleanup in case of error
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/continue-story/{request_id}")
async def continue_story(request_id: str):
    state = story_store.get(request_id)
    if not state:
        raise HTTPException(status_code=404, detail="Story not found")
    
    if len(state["generated_parts"]) < 1:
        # If the first part is not generated yet
        return {"status": "incomplete", "message": "First part not generated yet."}
    
    # Call OpenAI API to generate the second half of the story
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f"Continue the story based on the prompt: '{state['prompt']}' with around {state['word_count']} words. Complete the story."}
            ]
        )
        # Append the second part to the generated parts and include it in the response
        story_part = response["choices"][0]["message"]["content"]
        return {"status": "complete", "second_part": story_part}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


'''
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import openai

app = FastAPI()

# Mocked store for simplicity
story_store = {}

@app.post("/generate-story-comment")
async def generate_story(request: StoryRequest):
    request_id = str(len(story_store) + 1)
    
    # Store initial metadata
    story_store[request_id] = {"prompt": request.prompt, "word_count": request.word_count, "generated_parts": []}
    
    async def generate_story_stream():
        try:
            # Call OpenAI API with streaming enabled
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": f"Write a story based on the prompt: '{request.prompt}' with around {request.word_count} words. Start generating the story part by part."}
                ],
                stream=True  # Enable streaming
            )
            
            story = ""  # Variable to accumulate the full story
            for chunk in response:
                if 'choices' in chunk and chunk['choices']:
                    delta = chunk['choices'][0]['delta']
                    if 'content' in delta:
                        part = delta['content']
                        story += part
                        yield part  # Stream this part to the client
                        
            # Save the full story in the store after streaming is complete
            story_store[request_id]["generated_parts"].append(story)
            print(f"Story generation completed for Request ID: {request_id}")
        except Exception as e:
            # Cleanup in case of error
            story_store.pop(request_id, None)
            raise HTTPException(status_code=500, detail=str(e))
    
    # Return StreamingResponse
    return StreamingResponse(generate_story_stream(), media_type="text/plain")



'''