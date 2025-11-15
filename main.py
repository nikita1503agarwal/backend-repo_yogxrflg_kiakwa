import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from schemas import ContactMessage
from database import create_document

app = FastAPI(title="Artist Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Artist Portfolio API is running"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        from database import db

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

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# -------------------------
# Portfolio data endpoints
# -------------------------
class Project(BaseModel):
    title: str
    description: str
    image: str
    tags: List[str] = []
    link: Optional[str] = None


MOCK_PROJECTS: List[Project] = [
    Project(
        title="Neon Dreams",
        description="Exploration of light and shadow in a cyberpunk palette.",
        image="https://images.unsplash.com/photo-1517816743773-6e0fd518b4a6?q=80&w=1600&auto=format&fit=crop",
        tags=["3D", "Concept", "Futuristic"],
        link="#"
    ),
    Project(
        title="Waves of Code",
        description="Generative art driven by audio-reactive algorithms.",
        image="https://images.unsplash.com/photo-1517694712202-14dd9538aa97?q=80&w=1600&auto=format&fit=crop",
        tags=["Generative", "WebGL"],
        link="#"
    ),
    Project(
        title="Celestial Forms",
        description="Parametric sculptures inspired by orbital mechanics.",
        image="https://images.unsplash.com/photo-1549880338-65ddcdfd017b?q=80&w=1600&auto=format&fit=crop",
        tags=["Sculpt", "Parametric"],
        link="#"
    ),
]


@app.get("/projects", response_model=List[Project])
def list_projects():
    return MOCK_PROJECTS


# -------------------------
# Contact form submission
# -------------------------
@app.post("/contact")
def submit_contact(message: ContactMessage):
    try:
        inserted_id = create_document("contactmessage", message)
        return {"status": "ok", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
