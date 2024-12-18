from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from database import StoryResponse, DefaultStory, BannerResponse , Banner, MetadataResponse,GenreResponse,Genre
from database import SubGenreResponse,SubGenre, UserResponse , User
import openai
import os
from typing import Dict, Optional

app = FastAPI()


# Route to render an HTML page
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI app!"}


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
    
@app.get("/userinfo", response_model=UserResponse)
def get_user_info(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

'''OPEN AI INTEGRATION'''

story_store: Dict[str, dict[str, Optional[str]]] = {}


openai.api_key = "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"

# Request body model
class StoryRequest(BaseModel):
    prompt: str
    word_count: int

@app.post("/generate-story")
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