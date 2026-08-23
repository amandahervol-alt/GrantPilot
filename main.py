from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.routes import router as api_router
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = FastAPI(title="GrantPilot", description="AI-powered grant narrative assistant")

# Mount API routes
app.include_router(api_router, prefix="/api")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """Serve the main frontend application."""
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
