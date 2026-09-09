import os
import urllib.parse
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

# Database configuration
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB", "customer_retention")

# Enable MySQL if USE_MYSQL is true in .env
USE_MYSQL = os.getenv("USE_MYSQL", "false").lower() in ("true", "1", "yes")

if USE_MYSQL:
    # URL-encode password to handle special characters like '@' and '#' cleanly in SQLAlchemy
    encoded_pwd = urllib.parse.quote_plus(MYSQL_PASSWORD)
    DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{encoded_pwd}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
else:
    SQLITE_PATH = BASE_DIR / "retention_app.db"
    DATABASE_URL = f"sqlite:///{SQLITE_PATH}"

# Security / JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY", "customer_retention_super_secret_jwt_key_2026_x89f")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# ML Model Paths
MODEL_PATH = BASE_DIR / "best_churn_model.pkl"
FEATURE_COLUMNS_PATH = BASE_DIR / "model_feature_columns.pkl"

# CSV Data Paths
CLEANED_CSV_PATH = BASE_DIR / "DataSet" / "cleaned" / "E_Comm_Cleaned_Final.csv"
PREPROCESSED_CSV_PATH = BASE_DIR / "DataSet" / "preprocessed" / "E_Comm_Preprocessed.csv"
