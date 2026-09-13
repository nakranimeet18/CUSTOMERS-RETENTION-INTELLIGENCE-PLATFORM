from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL, USE_MYSQL, BASE_DIR

def get_connect_args(url: str):
    """Generate connection arguments, ensuring SSL support for remote MySQL (e.g. Aiven)."""
    if "sqlite" in url:
        return {"check_same_thread": False}
    elif "mysql" in url:
        # If connecting to remote cloud MySQL (not localhost), enable SSL support
        if "127.0.0.1" not in url and "localhost" not in url:
            return {
                "ssl": {
                    "check_hostname": False,
                    "verify_mode": 0
                }
            }
    return {}

def init_engine():
    """Initialize database engine with MySQL support and SQLite fallback."""
    global DATABASE_URL
    
    if USE_MYSQL:
        try:
            conn_args = get_connect_args(DATABASE_URL)
            temp_engine = create_engine(DATABASE_URL, connect_args=conn_args, pool_pre_ping=True)
            with temp_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(f"✅ Connected to MySQL Database successfully.")
            return temp_engine
        except Exception as e:
            print(f"⚠️ Could not connect to MySQL database ({e}).")
            print("👉 Please verify your Aiven or MySQL credentials in the environment variables.")
            print("🔄 Falling back to local SQLite database (retention_app.db)...")
            
            sqlite_url = f"sqlite:///{BASE_DIR / 'retention_app.db'}"
            DATABASE_URL = sqlite_url
            return create_engine(sqlite_url, connect_args={"check_same_thread": False}, pool_pre_ping=True)
    else:
        conn_args = get_connect_args(DATABASE_URL)
        return create_engine(DATABASE_URL, connect_args=conn_args, pool_pre_ping=True)

engine = init_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency to provide database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
