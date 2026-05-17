"""
Questions endpoints - daily questions and question bank.
"""
import random
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db import get_db
from app.core.time import now_str

router = APIRouter()


# Pydantic Schemas
class QuestionBankBase(BaseModel):
    content: str
    targetDate: Optional[str] = None


class QuestionBankCreate(QuestionBankBase):
    pass


class QuestionBankResponse(BaseModel):
    id: int
    content: str
    targetDate: Optional[str] = None
    createdAt: str

    class Config:
        from_attributes = True


class DailyQuestionResponse(BaseModel):
    id: int
    date: str
    content: str
    answerA: Optional[str] = None
    answerB: Optional[str] = None

    class Config:
        from_attributes = True


class AnswerRequest(BaseModel):
    answerA: Optional[str] = None
    answerB: Optional[str] = None


# Import legacy models
import sys
sys.path.insert(0, str(__file__).rsplit("/", 4)[0])

from database import DailyQuestion, QuestionBank


DEFAULT_QUESTIONS = [
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


@router.get("/today", response_model=DailyQuestionResponse)
def get_today_question(db: Session = Depends(get_db)):
    """Get today's question, generating one if needed."""
    today = date.today().strftime("%Y-%m-%d")

    # Check if we already have a question for today
    db_question = db.query(DailyQuestion).filter(DailyQuestion.date == today).first()

    if not db_question:
        # Generate a new question
        content = _generate_question(db)

        db_question = DailyQuestion(
            date=today,
            content=content
        )
        db.add(db_question)
        db.commit()
        db.refresh(db_question)

    return DailyQuestionResponse(
        id=db_question.id,
        date=db_question.date,
        content=db_question.content,
        answerA=db_question.answer_a,
        answerB=db_question.answer_b
    )


def _generate_question(db: Session) -> str:
    """Generate a question using priority: specific date > general bank > default."""
    today = date.today().strftime("%Y-%m-%d")

    # 1. Try specific date question
    target_question = db.query(QuestionBank).filter(
        QuestionBank.target_date == today
    ).first()
    if target_question:
        return target_question.content

    # 2. Random general question from bank
    general_questions = db.query(QuestionBank).filter(
        (QuestionBank.target_date == None) | (QuestionBank.target_date == "")
    ).all()
    if general_questions:
        return random.choice(general_questions).content

    # 3. Fallback to default questions
    return random.choice(DEFAULT_QUESTIONS)


@router.post("/today/answer")
def answer_question(answer: AnswerRequest, db: Session = Depends(get_db)):
    """Save answers to today's question."""
    today = date.today().strftime("%Y-%m-%d")
    db_question = db.query(DailyQuestion).filter(DailyQuestion.date == today).first()

    if not db_question:
        raise HTTPException(status_code=404, detail="No question for today")

    if answer.answerA is not None:
        db_question.answer_a = answer.answerA
    if answer.answerB is not None:
        db_question.answer_b = answer.answerB

    db.commit()

    return {"success": True}


@router.get("/history", response_model=List[DailyQuestionResponse])
def get_question_history(
    limit: int = 30,
    db: Session = Depends(get_db)
):
    """Get question history."""
    questions = db.query(DailyQuestion).order_by(
        text("date DESC")
    ).limit(limit).all()

    return [
        DailyQuestionResponse(
            id=q.id,
            date=q.date,
            content=q.content,
            answerA=q.answer_a,
            answerB=q.answer_b
        )
        for q in questions
    ]


@router.get("/bank", response_model=List[QuestionBankResponse])
def get_question_bank(db: Session = Depends(get_db)):
    """Get all questions in the question bank."""
    items = db.query(QuestionBank).order_by(text("created_at DESC")).all()

    return [
        QuestionBankResponse(
            id=item.id,
            content=item.content,
            targetDate=item.target_date,
            createdAt=item.created_at
        )
        for item in items
    ]


@router.post("/bank", response_model=QuestionBankResponse)
def create_question_bank_item(item: QuestionBankCreate, db: Session = Depends(get_db)):
    """Add a new question to the bank."""
    db_item = QuestionBank(
        content=item.content,
        target_date=item.targetDate,
        created_at=now_str()
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return QuestionBankResponse(
        id=db_item.id,
        content=db_item.content,
        targetDate=db_item.target_date,
        createdAt=db_item.created_at
    )


@router.put("/bank/{item_id}", response_model=QuestionBankResponse)
def update_question_bank_item(
    item_id: int,
    update: QuestionBankCreate,
    db: Session = Depends(get_db)
):
    """Update a question in the bank."""
    item = db.query(QuestionBank).filter(QuestionBank.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Question not found")

    item.content = update.content
    item.target_date = update.targetDate
    db.commit()
    db.refresh(item)

    return QuestionBankResponse(
        id=item.id,
        content=item.content,
        targetDate=item.target_date,
        createdAt=item.created_at
    )


@router.delete("/bank/{item_id}")
def delete_question_bank_item(item_id: int, db: Session = Depends(get_db)):
    """Delete a question from the bank."""
    item = db.query(QuestionBank).filter(QuestionBank.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Question not found")

    db.delete(item)
    db.commit()

    return {"success": True}