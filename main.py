from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from database import StoryResponse, DefaultStory, BannerResponse , Banner, MetadataResponse,GenreResponse,Genre
from database import SubGenreResponse,SubGenre

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


