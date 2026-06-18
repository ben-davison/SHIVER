from sqlalchemy import Column, Integer, String, Boolean, create_engine, DateTime, ForeignKey, Float
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import enum
from datetime import datetime

# 1. Setup Database (SQLite for simplicity)
# This will create a file named 'shiver_users.db' in your server folder
SQLALCHEMY_DATABASE_URL = "sqlite:///./shiver_users.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} # Needed for SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 2. User Table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    tour_status = Column(String, server_default="pending", nullable=False)
    downloads = relationship("DownloadLog", back_populates="user")



class DownloadLog(Base):
    __tablename__ = "download_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # What did they do? (e.g., 'cube_netcdf', 'map_click', 'file_upload', 'chart_export')
    interaction_type = Column(String, default="cube_netcdf")
    
    filename = Column(String)
    file_size_mb = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to User
    user = relationship("User", back_populates="downloads")
    
    
class TourStatus(str, enum.Enum):
    PENDING = "pending"                  # Brand new user, needs full tour (Intro + Advanced)
    INTRO_COMPLETED = "intro_completed"  # Completed guest tour, only needs Advanced tour
    COMPLETED = "completed"              # Fully finished everything
    NEVER_ASK_AGAIN = "never_ask_again"  # Opted out completely
    

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()