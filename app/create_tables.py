import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import engine, Base
import app.models  # Ensure all SQLAlchemy models are registered

print("🔨 Creating database tables...")
try:
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully!")
    print("Tables:", list(Base.metadata.tables.keys()))
except Exception as e:
    print(f"❌ Failed to create tables: {e}")
