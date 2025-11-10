import os
from typing import List, Optional, Any, Dict
from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Movie as MovieSchema

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Utility -----

def serialize_movie(doc: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(doc.get("_id")),
        "title": doc.get("title", ""),
        "description": doc.get("description", ""),
        "rating": float(doc.get("rating", 0)),
        "poster_url": doc.get("poster_url"),
        "genres": doc.get("genres"),
        "created_at": doc.get("created_at"),
        "updated_at": doc.get("updated_at"),
    }

# ----- Models -----

class MovieIn(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field("", max_length=2000)
    rating: float = Field(..., ge=0, le=10)
    poster_url: Optional[str] = None
    genres: Optional[List[str]] = None

class MovieUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    rating: Optional[float] = Field(None, ge=0, le=10)
    poster_url: Optional[str] = None
    genres: Optional[List[str]] = None

class MovieOut(MovieIn):
    id: str

# ----- Routes -----

@app.get("/")
def read_root():
    return {"message": "Movies API is running"}

@app.get("/api/movies", response_model=List[MovieOut])
def list_movies() -> List[MovieOut]:
    docs = get_documents("movie")
    return [MovieOut(**serialize_movie(d)) for d in docs]

@app.post("/api/movies", response_model=MovieOut)
def add_movie(payload: MovieIn) -> MovieOut:
    # Validate via schema as well
    MovieSchema(**payload.model_dump())
    inserted_id = create_document("movie", payload.model_dump())
    doc = db["movie"].find_one({"_id": ObjectId(inserted_id)})
    return MovieOut(**serialize_movie(doc))

@app.delete("/api/movies/{movie_id}")
def delete_movie(movie_id: str):
    try:
        oid = ObjectId(movie_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid movie id")
    result = db["movie"].delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"status": "ok"}

@app.put("/api/movies/{movie_id}", response_model=MovieOut)
def update_movie(movie_id: str, payload: MovieUpdate) -> MovieOut:
    try:
        oid = ObjectId(movie_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid movie id")

    update_data = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    db["movie"].update_one({"_id": oid}, {"$set": update_data})
    doc = db["movie"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Movie not found")
    return MovieOut(**serialize_movie(doc))

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
