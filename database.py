from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, JSON, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database connection
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://xxladmin:XXLadmin_2021!@127.0.0.1:3310/love_memory"

# Create database engine
# Note: We'll create the database if it doesn't exist, but SQLAlchemy needs to connect to an existing DB first.
# So we'll connect to 'mysql' database first to create 'love_memory'
temp_engine = create_engine("mysql+mysqlconnector://xxladmin:XXLadmin_2021!@127.0.0.1:3310/")
try:
    with temp_engine.connect() as conn:
        conn.execute(text("CREATE DATABASE IF NOT EXISTS love_memory DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
        conn.commit()
except Exception as e:
    print(f"Database creation warning (might already exist): {e}")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Models
class Info(Base):
    __tablename__ = "info"

    id = Column(Integer, primary_key=True, index=True)
    couple_name = Column(String(255))
    start_date = Column(String(50))
    next_anniversary = Column(String(50))
    today_mood = Column(String(255))

class Moment(Base):
    __tablename__ = "moments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    date = Column(String(50))
    location = Column(String(255))
    latitude = Column(String(50), nullable=True) # Stored as string to preserve precision if needed, or float
    longitude = Column(String(50), nullable=True)
    mood = Column(String(50))
    summary = Column(Text)
    images = Column(JSON)  # Stores list of image URLs
    has_video = Column(Boolean, default=False)

class BucketItem(Base):
    __tablename__ = "bucket_list"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    description = Column(Text, nullable=True)
    status = Column(String(50), default="pending")  # pending, planned, completed
    icon = Column(String(50), default="✨")
    images = Column(JSON, nullable=True) # Stores list of image URLs (e.g. proof of completion)
    created_at = Column(String(50))
    completed_at = Column(String(50), nullable=True)

class TimeCapsule(Base):
    __tablename__ = "time_capsules"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String(100)) # Who wrote this letter
    receiver = Column(String(100)) # Who is it for
    content = Column(Text)
    open_at = Column(String(50)) # Unlock date
    created_at = Column(String(50))
    is_opened = Column(Boolean, default=False)

class Music(Base):
    __tablename__ = "music"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    artist = Column(String(255))
    url = Column(String(500))
    cover = Column(String(500), nullable=True)

class Anniversary(Base):
    __tablename__ = "anniversaries"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    date = Column(String(50)) # e.g. "2023-05-20"
    type = Column(String(50)) # "anniversary" (repeat yearly) or "event" (one time)
    icon = Column(String(50), default="📅")

class CoverImage(Base):
    __tablename__ = "covers"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500))

class DailyQuestion(Base):
    __tablename__ = "daily_questions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(50)) # "2023-05-20"
    content = Column(String(500))
    answer_a = Column(Text, nullable=True)
    answer_b = Column(Text, nullable=True)

class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    type = Column(String(50))            # anniversary | capsule | question | bucket
    trigger_at = Column(String(50))      # ISO date string
    advance = Column(String(20), default="same_day")  # same_day | 1d | 3d
    repeat_rule = Column(String(50), default="none")  # none | daily | weekly | monthly | yearly
    channels = Column(JSON, default=list)             # ["in_app", "push", "email"]
    quiet_hours_start = Column(String(10), nullable=True)
    quiet_hours_end = Column(String(10), nullable=True)
    enabled = Column(Boolean, default=True)
    status = Column(String(20), default="pending")    # pending | done | ignored
    created_at = Column(String(50))

class QuestionBank(Base):
    __tablename__ = "question_bank"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(500))
    target_date = Column(String(50), nullable=True) # "2024-05-20" or None
    created_at = Column(String(50))

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
