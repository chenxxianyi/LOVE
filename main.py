from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, date
import calendar
import json
import os
import socket
import uuid

from database import engine, SessionLocal, Base, Info, Moment, BucketItem, TimeCapsule, Music, Anniversary, CoverImage, DailyQuestion, Reminder, QuestionBank, get_db
from love_core import router as core_router, init_p0_tables

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Create tables
try:
    # Use raw connection to ensure database exists first (handled in database.py)
    # Then bind engine to the specific database
    Base.metadata.create_all(bind=engine)
    init_p0_tables()
except Exception as e:
    print(f"Error creating tables: {e}")


app = FastAPI()
app.include_router(core_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Files
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# Pydantic Models
class InfoBase(BaseModel):
    coupleName: str
    todayMood: str

class InfoUpdate(InfoBase):
    pass

class DashboardStat(BaseModel):
    label: str
    value: str
    hint: str

class InfoResponse(InfoBase):
    dashboardStats: List[DashboardStat]

class MomentBase(BaseModel):
    title: str
    date: str
    location: str
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    mood: str
    summary: str
    images: List[str]
    hasVideo: bool

class MomentCreate(MomentBase):
    pass

class MomentResponse(MomentBase):
    id: int

    class Config:
        orm_mode = True

class BucketItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "pending"
    icon: str = "✨"
    images: Optional[List[str]] = []
    
class BucketItemCreate(BucketItemBase):
    pass

class BucketItemUpdate(BaseModel):
    status: Optional[str] = None
    images: Optional[List[str]] = None
    completed_at: Optional[str] = None

class BucketItemResponse(BucketItemBase):
    id: int
    created_at: str
    completed_at: Optional[str] = None

    class Config:
        orm_mode = True

class TimeCapsuleBase(BaseModel):
    sender: str
    receiver: str
    content: str
    open_at: str

class TimeCapsuleCreate(TimeCapsuleBase):
    pass

class TimeCapsuleResponse(TimeCapsuleBase):
    id: int
    created_at: str
    is_opened: bool
    # We might want to hide content if it's locked, but for simplicity we'll handle that in logic or frontend
    # Better: return content only if unlocked

    class Config:
        orm_mode = True

class MusicBase(BaseModel):
    title: str
    artist: str
    url: str
    cover: Optional[str] = None

class MusicCreate(MusicBase):
    pass

class MusicResponse(MusicBase):
    id: int

    class Config:
        orm_mode = True

class AnniversaryBase(BaseModel):
    title: str
    date: str
    type: str # "anniversary" or "event"
    icon: str = "📅"

class AnniversaryCreate(AnniversaryBase):
    pass

class AnniversaryResponse(AnniversaryBase):
    id: int
    days_left: Optional[int] = 0

    class Config:
        orm_mode = True

class CoverImageBase(BaseModel):
    url: str

class CoverImageCreate(CoverImageBase):
    pass

class CoverImageResponse(CoverImageBase):
    id: int

    class Config:
        orm_mode = True

class ReportResponse(BaseModel):
    total_moments: int
    top_mood: Optional[str]
    total_locations: int
    total_images: int
    days_together: int
    latest_moment_date: Optional[str]

class DailyQuestionResponse(BaseModel):
    id: int
    date: str
    content: str
    answer_a: Optional[str] = None
    answer_b: Optional[str] = None

    class Config:
        from_attributes = True

class QuestionBankBase(BaseModel):
    content: str
    target_date: Optional[str] = None

class QuestionBankCreate(QuestionBankBase):
    pass

class QuestionBankResponse(QuestionBankBase):
    id: int
    created_at: str
    
    class Config:
        from_attributes = True

class ReminderBase(BaseModel):
    pass

class DailyQuestionBase(BaseModel):
    content: str
    date: str
    answer_a: Optional[str] = None
    answer_b: Optional[str] = None

class DailyQuestionCreate(DailyQuestionBase):
    pass

class DailyQuestionResponse(DailyQuestionBase):
    id: int

    class Config:
        orm_mode = True

# Helper functions
def get_days_diff(start_date_str: str) -> int:
    try:
        start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        now = date.today()
        return abs((now - start).days)
    except:
        return 0

def get_next_anniversary_days(start_date_str: str) -> int:
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        today = date.today()
        start_month = start_date.month
        start_day = start_date.day

        def safe_anniversary(year: int) -> date:
            # Handle 2/29 and other month day edge cases
            last_day = calendar.monthrange(year, start_month)[1]
            return date(year, start_month, min(start_day, last_day))

        anniversary_this_year = safe_anniversary(today.year)
        if today <= anniversary_this_year:
            next_anniversary = anniversary_this_year
        else:
            next_anniversary = safe_anniversary(today.year + 1)

        return (next_anniversary - today).days
    except:
        return 0

# Seed Data
@app.on_event("startup")
def seed_data():
    db = SessionLocal()
    try:
        # Check if info exists
        info = db.query(Info).first()
        if not info:
            new_info = Info(
                couple_name="小鹿 & 小棠",
                start_date="2024-04-21",
                next_anniversary="2026-03-21",
                today_mood="今天也要认真相爱"
            )
            db.add(new_info)
            db.commit()

        # Check if moments exist
        if db.query(Moment).count() == 0:
            moments_data = [
                {
                    "title": "海边日落散步",
                    "date": "2026-02-14 18:20",
                    "location": "青岛石老人海水浴场",
                    "mood": "心动",
                    "summary": "风很柔，海浪很慢。你说以后每年都要来一次海边，我们在落日下拍了很多张笨拙但好看的合照。",
                    "images": [
                        "https://images.unsplash.com/photo-1473116763249-2faaef81ccda?auto=format&fit=crop&w=1200&q=80",
                        "https://images.unsplash.com/photo-1495567720989-cebdbdd97913?auto=format&fit=crop&w=1200&q=80",
                    ],
                    "has_video": True,
                },
                {
                    "title": "凌晨厨房小夜宵",
                    "date": "2026-01-22 00:42",
                    "location": "家里",
                    "mood": "治愈",
                    "summary": "临时起意煮了面，番茄和鸡蛋都切得歪歪扭扭。你说这比任何餐厅都好吃，因为是我们一起做的。",
                    "images": [
                        "https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=1200&q=80",
                    ],
                    "has_video": False,
                },
                {
                    "title": "第一次一起看雪",
                    "date": "2025-12-09 21:15",
                    "location": "南京玄武湖",
                    "mood": "浪漫",
                    "summary": "雪落在围巾和肩膀上，手机镜头雾蒙蒙的。我们拍了十几段短视频，决定做成年度回忆片。",
                    "images": [
                        "https://images.unsplash.com/photo-1453306458620-5bbef13a5bca?auto=format&fit=crop&w=1200&q=80",
                        "https://images.unsplash.com/photo-1515792677823-30f151e09dcd?auto=format&fit=crop&w=1200&q=80",
                    ],
                    "has_video": True,
                },
            ]
            
            for m in moments_data:
                db_moment = Moment(
                    title=m["title"],
                    date=m["date"],
                    location=m["location"],
                    mood=m["mood"],
                    summary=m["summary"],
                    images=m["images"], # SQLAlchemy JSON type handles serialization automatically
                    has_video=m["has_video"]
                )
                db.add(db_moment)
            db.commit()
    except Exception as e:
        print(f"Seeding error: {e}")
    finally:
        db.close()

# Routes
@app.get("/api/info")
def get_info(db: Session = Depends(get_db)):
    info = db.query(Info).first()
    if not info:
        # Create default info if not exists
        info = Info(
            couple_name="小鹿 & 小棠", 
            start_date="2024-04-21",
            cover_image=""
        )
        db.add(info)
        db.commit()
        db.refresh(info)
        
    # Calculate days together
    start = datetime.strptime(info.start_date, "%Y-%m-%d").date()
    today = date.today()
    days_together = (today - start).days
    
    # Calculate next month anniversary
    try:
        next_month_date = date(today.year, today.month, start.day)
        if next_month_date < today:
            if today.month == 12:
                next_month_date = date(today.year + 1, 1, start.day)
            else:
                next_month_date = date(today.year, today.month + 1, start.day)
        days_left = (next_month_date - today).days
    except ValueError:
        days_left = 30 

    return {
        "coupleName": info.couple_name,
        "todayMood": "今天也要认真相爱",
        "dashboardStats": [
            {"label": "在一起", "value": f"{days_together} 天", "hint": f"从 {info.start_date} 到今天"},
            {"label": "共同回忆", "value": f"{db.query(Moment).count()} 条", "hint": "照片 + 视频 + 文字"},
            {"label": "纪念日倒计时", "value": f"{days_left} 天", "hint": "下一次月纪念日"}
        ],
        "start_date": info.start_date
    }

class InfoUpdate(BaseModel):
    couple_names: Optional[str] = None
    start_date: Optional[str] = None

@app.post("/api/info", response_model=dict)
def update_info(info_update: InfoUpdate, db: Session = Depends(get_db)):
    db_info = db.query(Info).first()
    if not db_info:
        db_info = Info(
            couple_name="小鹿 & 小棠", 
            start_date="2024-04-21",
            cover_image=""
        )
        db.add(db_info)
    
    if info_update.couple_names:
        db_info.couple_name = info_update.couple_names
    if info_update.start_date:
        db_info.start_date = info_update.start_date
        
    db.commit()
    db.refresh(db_info)
    return {"success": True}

@app.get("/api/moments", response_model=List[MomentResponse])
def get_moments(db: Session = Depends(get_db)):
    moments = db.query(Moment).order_by(text("date DESC")).all()
    # Map database fields to Pydantic model (snake_case to camelCase mapping handled manually or by config)
    return [
        MomentResponse(
            id=m.id,
            title=m.title,
            date=m.date,
            location=m.location,
            latitude=m.latitude,
            longitude=m.longitude,
            mood=m.mood,
            summary=m.summary,
            images=m.images if m.images else [],
            hasVideo=m.has_video
        ) for m in moments
    ]

@app.post("/api/moments", response_model=MomentResponse)
def create_moment(moment: MomentCreate, db: Session = Depends(get_db)):
    db_moment = Moment(
        title=moment.title,
        date=moment.date,
        location=moment.location,
        latitude=moment.latitude,
        longitude=moment.longitude,
        mood=moment.mood,
        summary=moment.summary,
        images=moment.images,
        has_video=moment.hasVideo
    )
    db.add(db_moment)
    db.commit()
    db.refresh(db_moment)
    
    return MomentResponse(
        id=db_moment.id,
        title=db_moment.title,
        date=db_moment.date,
        location=db_moment.location,
        latitude=db_moment.latitude,
        longitude=db_moment.longitude,
        mood=db_moment.mood,
        summary=db_moment.summary,
        images=db_moment.images if db_moment.images else [],
        hasVideo=db_moment.has_video
    )

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Generate unique filename
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOADS_DIR, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            
        # Return URL
        return {"url": f"http://localhost:8000/uploads/{unique_filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class MomentUpdate(BaseModel):
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    title: Optional[str] = None
    date: Optional[str] = None
    location: Optional[str] = None
    mood: Optional[str] = None
    summary: Optional[str] = None
    images: Optional[List[str]] = None
    hasVideo: Optional[bool] = None

@app.put("/api/moments/{moment_id}", response_model=MomentResponse)
def update_moment(moment_id: int, update: MomentUpdate, db: Session = Depends(get_db)):
    db_moment = db.query(Moment).filter(Moment.id == moment_id).first()
    if not db_moment:
        raise HTTPException(status_code=404, detail="Moment not found")
    
    if update.latitude is not None:
        db_moment.latitude = update.latitude
    if update.longitude is not None:
        db_moment.longitude = update.longitude
    if update.title is not None:
        db_moment.title = update.title
    if update.date is not None:
        db_moment.date = update.date
    if update.location is not None:
        db_moment.location = update.location
    if update.mood is not None:
        db_moment.mood = update.mood
    if update.summary is not None:
        db_moment.summary = update.summary
    if update.images is not None:
        db_moment.images = update.images
    if update.hasVideo is not None:
        db_moment.has_video = update.hasVideo
        
    db.commit()
    db.refresh(db_moment)
    return MomentResponse(
        id=db_moment.id,
        title=db_moment.title,
        date=db_moment.date,
        location=db_moment.location,
        latitude=db_moment.latitude,
        longitude=db_moment.longitude,
        mood=db_moment.mood,
        summary=db_moment.summary,
        images=db_moment.images if db_moment.images else [],
        hasVideo=db_moment.has_video
    )

@app.delete("/api/moments/{moment_id}")
def delete_moment(moment_id: int, db: Session = Depends(get_db)):
    db_moment = db.query(Moment).filter(Moment.id == moment_id).first()
    if not db_moment:
        raise HTTPException(status_code=404, detail="Moment not found")
    db.delete(db_moment)
    db.commit()
    return {"success": True}

# Bucket List Routes
@app.get("/api/bucket", response_model=List[BucketItemResponse])
def get_bucket_list(db: Session = Depends(get_db)):
    items = db.query(BucketItem).order_by(text("id DESC")).all()
    return [
        BucketItemResponse(
            id=item.id,
            title=item.title,
            description=item.description,
            status=item.status,
            icon=item.icon,
            images=item.images if item.images else [],
            created_at=item.created_at,
            completed_at=item.completed_at
        ) for item in items
    ]

@app.post("/api/bucket", response_model=BucketItemResponse)
def create_bucket_item(item: BucketItemCreate, db: Session = Depends(get_db)):
    db_item = BucketItem(
        title=item.title,
        description=item.description,
        status=item.status,
        icon=item.icon,
        images=item.images,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    return BucketItemResponse(
        id=db_item.id,
        title=db_item.title,
        description=db_item.description,
        status=db_item.status,
        icon=db_item.icon,
        images=db_item.images if db_item.images else [],
        created_at=db_item.created_at,
        completed_at=db_item.completed_at
    )

@app.put("/api/bucket/{item_id}", response_model=BucketItemResponse)
def update_bucket_item(item_id: int, item_update: BucketItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(BucketItem).filter(BucketItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Bucket item not found")
        
    if item_update.status:
        db_item.status = item_update.status
        if item_update.status == "completed" and not db_item.completed_at:
             db_item.completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if item_update.images:
        db_item.images = item_update.images
        
    if item_update.completed_at:
        db_item.completed_at = item_update.completed_at
        
    db.commit()
    db.refresh(db_item)
    
    return BucketItemResponse(
        id=db_item.id,
        title=db_item.title,
        description=db_item.description,
        status=db_item.status,
        icon=db_item.icon,
        images=db_item.images if db_item.images else [],
        created_at=db_item.created_at,
        completed_at=db_item.completed_at
    )

# Time Capsule Routes
@app.get("/api/capsules", response_model=List[TimeCapsuleResponse])
def get_capsules(db: Session = Depends(get_db)):
    capsules = db.query(TimeCapsule).order_by(text("open_at ASC")).all()
    # Mask content if not yet openable (simple logic)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    results = []
    for c in capsules:
        is_unlocked = c.open_at <= now
        results.append(TimeCapsuleResponse(
            id=c.id,
            sender=c.sender,
            receiver=c.receiver,
            content=c.content if is_unlocked else "🔒 封印中...",
            open_at=c.open_at,
            created_at=c.created_at,
            is_opened=is_unlocked
        ))
    return results

@app.post("/api/capsules", response_model=TimeCapsuleResponse)
def create_capsule(capsule: TimeCapsuleCreate, db: Session = Depends(get_db)):
    db_capsule = TimeCapsule(
        sender=capsule.sender,
        receiver=capsule.receiver,
        content=capsule.content,
        open_at=capsule.open_at,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        is_opened=False
    )
    db.add(db_capsule)
    db.commit()
    db.refresh(db_capsule)
    
    return TimeCapsuleResponse(
        id=db_capsule.id,
        sender=db_capsule.sender,
        receiver=db_capsule.receiver,
        content=db_capsule.content,
        open_at=db_capsule.open_at,
        created_at=db_capsule.created_at,
        is_opened=False
    )

# Music Routes
@app.get("/api/music", response_model=List[MusicResponse])
def get_music_list(db: Session = Depends(get_db)):
    return db.query(Music).all()

@app.post("/api/music", response_model=MusicResponse)
def add_music(music: MusicCreate, db: Session = Depends(get_db)):
    db_music = Music(
        title=music.title,
        artist=music.artist,
        url=music.url,
        cover=music.cover
    )
    db.add(db_music)
    db.commit()
    db.refresh(db_music)
    return db_music

@app.delete("/api/music/{music_id}")
def delete_music(music_id: int, db: Session = Depends(get_db)):
    db_music = db.query(Music).filter(Music.id == music_id).first()
    if not db_music:
        raise HTTPException(status_code=404, detail="Music not found")
    db.delete(db_music)
    db.commit()
    return {"success": True}

# Anniversary Routes
@app.get("/api/anniversaries", response_model=List[AnniversaryResponse])
def get_anniversaries(db: Session = Depends(get_db)):
    anniversaries = db.query(Anniversary).all()
    results = []
    
    for a in anniversaries:
        days = 0
        if a.type == "anniversary":
            # Recurring yearly
            days = get_next_anniversary_days(a.date)
        else:
            # One time event
            try:
                target = datetime.strptime(a.date, "%Y-%m-%d").date()
                today = date.today()
                days = (target - today).days
            except:
                days = 0
                
        results.append(AnniversaryResponse(
            id=a.id,
            title=a.title,
            date=a.date,
            type=a.type,
            icon=a.icon,
            days_left=days
        ))
        
    # Sort by days left (nearest first)
    results.sort(key=lambda x: x.days_left if x.days_left >= 0 else 9999)
    return results

@app.post("/api/anniversaries", response_model=AnniversaryResponse)
def create_anniversary(anniversary: AnniversaryCreate, db: Session = Depends(get_db)):
    db_anniversary = Anniversary(
        title=anniversary.title,
        date=anniversary.date,
        type=anniversary.type,
        icon=anniversary.icon
    )
    db.add(db_anniversary)
    db.commit()
    db.refresh(db_anniversary)
    
    # Calculate initial days left
    days = 0
    if db_anniversary.type == "anniversary":
        days = get_next_anniversary_days(db_anniversary.date)
    else:
        try:
            target = datetime.strptime(db_anniversary.date, "%Y-%m-%d").date()
            today = date.today()
            days = (target - today).days
        except:
            days = 0

    return AnniversaryResponse(
        id=db_anniversary.id,
        title=db_anniversary.title,
        date=db_anniversary.date,
        type=db_anniversary.type,
        icon=db_anniversary.icon,
        days_left=days
    )

@app.delete("/api/anniversaries/{id}")
def delete_anniversary(id: int, db: Session = Depends(get_db)):
    db_item = db.query(Anniversary).filter(Anniversary.id == id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(db_item)
    db.commit()
    return {"success": True}

# Cover Image Routes
@app.get("/api/covers", response_model=List[CoverImageResponse])
def get_covers(db: Session = Depends(get_db)):
    return db.query(CoverImage).all()

@app.post("/api/covers", response_model=CoverImageResponse)
def add_cover(cover: CoverImageCreate, db: Session = Depends(get_db)):
    db_cover = CoverImage(url=cover.url)
    db.add(db_cover)
    db.commit()
    db.refresh(db_cover)
    return db_cover

@app.delete("/api/covers/{id}")
def delete_cover(id: int, db: Session = Depends(get_db)):
    db_cover = db.query(CoverImage).filter(CoverImage.id == id).first()
    if not db_cover:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(db_cover)
    db.commit()
    return {"success": True}

# Daily Question Routes
@app.get("/api/questions/today", response_model=DailyQuestionResponse)
def get_today_question(db: Session = Depends(get_db)):
    today = date.today().strftime("%Y-%m-%d")
    db_question = db.query(DailyQuestion).filter(DailyQuestion.date == today).first()
    
    if not db_question:
        import random
        # 1. 尝试寻找为今天【指定】的专属题库
        target_question = db.query(QuestionBank).filter(QuestionBank.target_date == today).first()
        if target_question:
            content = target_question.content
        else:
            # 2. 没有指定问题，则从普通未指定日期的通用自定义题库中随机抽题
            general_questions = db.query(QuestionBank).filter(
                (QuestionBank.target_date == None) | (QuestionBank.target_date == "")
            ).all()
            if general_questions:
                content = random.choice(general_questions).content
            else:
                # 3. 自定义题库里什么都没有，降级到内置保底默认题库
                questions = [
                    "如果中彩票了第一件事做什么？",
                    "你最喜欢我哪一点？",
                    "如果可以穿越时空，你想去哪里？",
                    "我们第一次见面的场景你还记得吗？",
                    "你觉得我们最默契的一件事是什么？",
                    "最近一次让你感动的事情是什么？",
                    "如果我们要一起养一只宠物，你会选什么？",
                    "你觉得完美的周末应该怎么过？",
                    "如果世界末日来了，你想吃什么？",
                    "你最想和我一起完成的愿望是什么？"
                ]
                content = random.choice(questions)
                
        db_question = DailyQuestion(date=today, content=content)
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        
    return db_question

@app.get("/api/question_bank", response_model=List[QuestionBankResponse])
def get_question_bank(db: Session = Depends(get_db)):
    return db.query(QuestionBank).order_by(text("created_at DESC")).all()

@app.post("/api/question_bank", response_model=QuestionBankResponse)
def create_question_bank(item: QuestionBankCreate, db: Session = Depends(get_db)):
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db_item = QuestionBank(
        content=item.content,
        target_date=item.target_date,
        created_at=created_at
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.put("/api/question_bank/{id}", response_model=QuestionBankResponse)
def update_question_bank(id: int, item: QuestionBankCreate, db: Session = Depends(get_db)):
    db_item = db.query(QuestionBank).filter(QuestionBank.id == id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Not found")
    
    db_item.content = item.content
    db_item.target_date = item.target_date
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/api/question_bank/{id}")
def delete_question_bank(id: int, db: Session = Depends(get_db)):
    db_item = db.query(QuestionBank).filter(QuestionBank.id == id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Not found")
    
    db.delete(db_item)
    db.commit()
    return {"success": True}

@app.post("/api/questions/{id}/answer", response_model=DailyQuestionResponse)
def answer_question(id: int, answer: dict, db: Session = Depends(get_db)):
    db_question = db.query(DailyQuestion).filter(DailyQuestion.id == id).first()
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")
        
    if "answer_a" in answer:
        db_question.answer_a = answer["answer_a"]
    if "answer_b" in answer:
        db_question.answer_b = answer["answer_b"]
        
    db.commit()
    db.refresh(db_question)
    return db_question

@app.get("/api/questions/history", response_model=List[DailyQuestionResponse])
def get_question_history(db: Session = Depends(get_db)):
    return db.query(DailyQuestion).order_by(text("date DESC")).all()

# Report Routes
@app.get("/api/report", response_model=ReportResponse)
def get_report(db: Session = Depends(get_db)):
    moments = db.query(Moment).all()
    
    total_moments = len(moments)
    
    # Calculate top mood
    mood_counts = {}
    for m in moments:
        mood_counts[m.mood] = mood_counts.get(m.mood, 0) + 1
    top_mood = max(mood_counts, key=mood_counts.get) if mood_counts else None
    
    # Calculate unique locations
    locations = set(m.location for m in moments if m.location)
    total_locations = len(locations)
    
    # Calculate total images
    total_images = sum(len(m.images) if m.images else 0 for m in moments)
    
    # Calculate days together (assuming start from first moment or today if none)
    # Ideally this should come from Info table, but we'll use first moment for now
    dates = [m.date for m in moments if m.date]
    if dates:
        dates.sort()
        first_date = datetime.strptime(dates[0], "%Y-%m-%d %H:%M").date()
        today = date.today()
        days_together = (today - first_date).days
        latest_moment_date = dates[-1]
    else:
        days_together = 0
        latest_moment_date = None
        
    return ReportResponse(
        total_moments=total_moments,
        top_mood=top_mood,
        total_locations=total_locations,
        total_images=total_images,
        days_together=days_together,
        latest_moment_date=latest_moment_date
    )


@app.get("/api/dashboard/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    def safe_count(table_name: str) -> int:
        try:
            value = db.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            return int(value or 0)
        except Exception:
            return 0

    info = db.query(Info).first()
    days_together = 0
    if info and info.start_date:
        try:
            start = datetime.strptime(info.start_date, "%Y-%m-%d").date()
            days_together = (date.today() - start).days
        except Exception:
            days_together = 0

    total_moments = safe_count("moments")
    total_bucket_items = safe_count("bucket_list")
    total_anniversaries = safe_count("anniversaries")
    total_capsules = safe_count("time_capsules")
    try:
        pending_value = db.execute(
            text("SELECT COUNT(*) FROM bucket_list WHERE status <> 'completed'")
        ).scalar()
        pending_bucket_items = int(pending_value or 0)
    except Exception:
        pending_bucket_items = 0

    # Keep both snake_case and camelCase for old/new frontends.
    return {
        "days_together": days_together,
        "total_moments": total_moments,
        "total_bucket_items": total_bucket_items,
        "pending_bucket_items": pending_bucket_items,
        "total_anniversaries": total_anniversaries,
        "total_capsules": total_capsules,
        "daysTogether": days_together,
        "totalMoments": total_moments,
        "totalBucketItems": total_bucket_items,
        "pendingBucketItems": pending_bucket_items,
        "totalAnniversaries": total_anniversaries,
        "totalCapsules": total_capsules,
    }


@app.get("/api/patterns")
def get_patterns(db: Session = Depends(get_db)):
    mood_counts = {}
    month_counts = {}
    location_counts = {}
    try:
        rows = db.execute(text("SELECT mood, date, location FROM moments")).fetchall()
    except Exception:
        rows = []

    for mood, moment_date, location in rows:
        if mood:
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
        if moment_date and len(moment_date) >= 7:
            month_key = moment_date[:7]
            month_counts[month_key] = month_counts.get(month_key, 0) + 1
        if location:
            location_counts[location] = location_counts.get(location, 0) + 1

    mood_patterns = [
        {"name": key, "count": value}
        for key, value in sorted(mood_counts.items(), key=lambda x: x[1], reverse=True)
    ]
    monthly_patterns = [
        {"month": key, "count": value}
        for key, value in sorted(month_counts.items(), key=lambda x: x[0])
    ]
    location_patterns = [
        {"name": key, "count": value}
        for key, value in sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    ]

    return {
        "mood_patterns": mood_patterns,
        "monthly_patterns": monthly_patterns,
        "location_patterns": location_patterns,
        "patterns": mood_patterns,
    }

if __name__ == "__main__":
    import uvicorn

    preferred_port = int(os.getenv("APP_PORT", "8000"))
    selected_port = preferred_port

    def _is_port_in_use(port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            return sock.connect_ex(("127.0.0.1", port)) == 0

    if _is_port_in_use(preferred_port):
        for candidate in range(preferred_port + 1, preferred_port + 20):
            if not _is_port_in_use(candidate):
                selected_port = candidate
                print(f"Port {preferred_port} is in use, fallback to {selected_port}.")
                break

    uvicorn.run(app, host="0.0.0.0", port=selected_port)
