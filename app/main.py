from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager
from pathlib import Path

from app.database import engine, Base
from app.routers import auth_router, users_router, admin_router
from app.csv_loader import CSVDataLoader

BASE_PROJECT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_PROJECT_DIR / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown actions."""
    print("🚀 Initializing Customer Retention Intelligence Platform FastAPI Backend...")
    # Create all database tables automatically on startup
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully.")
    
    # Pre-cache CSV user dataset & ML predictions
    CSVDataLoader.load_csv_users(limit=50)
    print("✅ Ready to serve requests.")
    yield
    print("👋 Shutting down FastAPI Backend application.")


app = FastAPI(
    title="Customer Retention Intelligence Platform API",
    description="AI-Powered Customer Churn Prediction, Explainability, and Retention Offer Engine",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for Frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from starlette.middleware.base import BaseHTTPMiddleware
class NoCacheStaticMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        path = request.url.path
        if path.endswith((".html", ".css", ".js")) or "/user" in path:
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

app.add_middleware(NoCacheStaticMiddleware)

# Include API Routers
app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(admin_router.router)


@app.get("/api/health", tags=["Health"])
def health_check():
    """API health check endpoint."""
    return {
        "status": "online",
        "platform": "Customer Retention Intelligence Platform API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }


# Mount Static Frontend Directories
if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="assets")
    app.mount("/admin", StaticFiles(directory=str(FRONTEND_DIR / "admin"), html=True), name="admin_pages")
    app.mount("/user", StaticFiles(directory=str(FRONTEND_DIR / "user"), html=True), name="user_pages")
    app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend_root")


@app.get("/login.html", tags=["Frontend"])
def login_page():
    login_file = FRONTEND_DIR / "login.html"
    if login_file.exists():
        return FileResponse(str(login_file))
    return JSONResponse(status_code=404, content={"message": "login.html not found"})


@app.get("/register.html", tags=["Frontend"])
def register_page():
    reg_file = FRONTEND_DIR / "register.html"
    if reg_file.exists():
        return FileResponse(str(reg_file))
    return JSONResponse(status_code=404, content={"message": "register.html not found"})


@app.get("/", tags=["Frontend"])
def root():
    """Default landing experience - serves the main landing page (defaults towards admin)."""
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {
        "status": "online",
        "platform": "Customer Retention Intelligence Platform API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }
