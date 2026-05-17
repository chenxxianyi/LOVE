"""
API v1 router - aggregates all domain routers.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, couple, memories, bucket, capsules, anniversaries, questions, media, reports

api_router = APIRouter()

# Include all domain routers
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(couple.router, prefix="/couple-space", tags=["情侣空间"])
api_router.include_router(memories.router, prefix="/moments", tags=["回忆"])
api_router.include_router(bucket.router, prefix="/bucket", tags=["愿望清单"])
api_router.include_router(capsules.router, prefix="/capsules", tags=["时光胶囊"])
api_router.include_router(anniversaries.router, prefix="/anniversaries", tags=["纪念日"])
api_router.include_router(questions.router, prefix="/questions", tags=["每日问答"])
api_router.include_router(media.router, prefix="/media", tags=["媒体"])
api_router.include_router(reports.router, prefix="/report", tags=["报告"])

router = api_router