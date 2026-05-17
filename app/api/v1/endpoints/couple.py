"""
Couple space endpoints - create, invite, join couple spaces.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import generate_invite_code, calculate_expiry
from app.core.time import now_str

router = APIRouter()


# Pydantic Schemas
class CreateSpaceRequest(BaseModel):
    spaceName: str
    startDate: str
    nickname: Optional[str] = None


class JoinSpaceRequest(BaseModel):
    inviteCode: str
    nickname: Optional[str] = None


class UpdateMemberRequest(BaseModel):
    nickname: Optional[str] = None


# Import P0 models
import sys
sys.path.insert(0, str(__file__).rsplit("/", 4)[0])

from love_core.models import P0User, P0CoupleSpace, P0CoupleMember, P0CoupleInvite, P0UnbindRequest


def get_current_user_id(authorization: str = None, db: Session = Depends(get_db)) -> int:
    """Extract current user ID from authorization."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization")

    from app.core.security import hash_token

    token = authorization.replace("Bearer ", "")
    token_hash = hash_token(token)

    from love_core.models import P0Session
    session = db.query(P0Session).filter(
        P0Session.access_token == token_hash,
        P0Session.revoked == False
    ).first()

    if not session:
        raise HTTPException(status_code=401, detail="Invalid token")

    return session.user_id


def get_user_couple_space(db: Session, user_id: int) -> Optional[dict]:
    """Get user's couple space with member info."""
    member = db.query(P0CoupleMember).filter(P0CoupleMember.user_id == user_id).first()
    if not member:
        return None

    space = db.query(P0CoupleSpace).filter(P0CoupleSpace.id == member.space_id).first()
    if not space:
        return None

    # Get partner info
    partner = db.query(P0CoupleMember).filter(
        P0CoupleMember.space_id == space.id,
        P0CoupleMember.user_id != user_id
    ).first()

    partner_info = None
    if partner:
        partner_user = db.query(P0User).filter(P0User.id == partner.user_id).first()
        if partner_user:
            partner_info = {
                "userId": partner.user_id,
                "nickname": partner.nickname,
                "avatar": partner_user.avatar
            }

    return {
        "spaceId": space.id,
        "spaceName": space.space_name,
        "startDate": space.start_date,
        "role": member.role,
        "nickname": member.nickname,
        "partner": partner_info,
        "joinedAt": member.joined_at
    }


@router.post("/create", response_model=dict)
def create_couple_space(
    req: CreateSpaceRequest,
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Create a new couple space and become the first member."""
    user_id = get_current_user_id(authorization, db)

    # Check if user already has a space
    existing = db.query(P0CoupleMember).filter(P0CoupleMember.user_id == user_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="User already in a couple space")

    # Create space
    space = P0CoupleSpace(
        space_name=req.spaceName,
        start_date=req.startDate,
        created_by=user_id,
        created_at=now_str()
    )
    db.add(space)
    db.commit()
    db.refresh(space)

    # Add creator as first member
    member = P0CoupleMember(
        space_id=space.id,
        user_id=user_id,
        nickname=req.nickname or "Partner A",
        role="owner"
    )
    db.add(member)
    db.commit()

    return {
        "spaceId": space.id,
        "spaceName": space.space_name,
        "startDate": space.start_date,
        "inviteCode": None
    }


@router.get("/me", response_model=dict)
def get_my_space(
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Get current user's couple space."""
    user_id = get_current_user_id(authorization, db)
    space_info = get_user_couple_space(db, user_id)

    if not space_info:
        return {"hasSpace": False, "space": None}

    return {
        "hasSpace": True,
        "space": space_info
    }


@router.post("/generate-invite", response_model=dict)
def generate_invite(
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Generate an invite code for partner to join."""
    user_id = get_current_user_id(authorization, db)
    space_info = get_user_couple_space(db, user_id)

    if not space_info:
        raise HTTPException(status_code=400, detail="User not in any couple space")

    space_id = space_info["spaceId"]

    # Check if space already has 2 members
    member_count = db.query(P0CoupleMember).filter(
        P0CoupleMember.space_id == space_id
    ).count()

    if member_count >= 2:
        raise HTTPException(status_code=400, detail="Space already has 2 members")

    # Generate new invite code
    code = generate_invite_code()
    expires_at = calculate_expiry(days=7)

    invite = P0CoupleInvite(
        space_id=space_id,
        code=code,
        expires_at=expires_at.strftime("%Y-%m-%d %H:%M:%S"),
        created_by=user_id
    )
    db.add(invite)
    db.commit()

    return {
        "inviteCode": code,
        "expiresAt": expires_at.strftime("%Y-%m-%d %H:%M:%S")
    }


@router.post("/join", response_model=dict)
def join_couple_space(
    req: JoinSpaceRequest,
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Join an existing couple space using invite code."""
    user_id = get_current_user_id(authorization, db)

    # Check if user already has a space
    existing = db.query(P0CoupleMember).filter(P0CoupleMember.user_id == user_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="User already in a couple space")

    # Find valid invite
    invite = db.query(P0CoupleInvite).filter(
        P0CoupleInvite.code == req.inviteCode.upper(),
        P0CoupleInvite.used == False
    ).first()

    if not invite:
        raise HTTPException(status_code=400, detail="Invalid or expired invite code")

    expires_at = datetime.strptime(invite.expires_at, "%Y-%m-%d %H:%M:%S")
    if datetime.now() > expires_at:
        raise HTTPException(status_code=400, detail="Invite code expired")

    # Mark invite as used
    invite.used = True
    invite.used_by = user_id

    # Add user to space
    member = P0CoupleMember(
        space_id=invite.space_id,
        user_id=user_id,
        nickname=req.nickname or "Partner B",
        role="member"
    )
    db.add(member)
    db.commit()

    # Get space info
    space = db.query(P0CoupleSpace).filter(P0CoupleSpace.id == invite.space_id).first()

    return {
        "success": True,
        "spaceId": space.id,
        "spaceName": space.space_name
    }


@router.delete("/leave")
def leave_couple_space(
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Leave the current couple space (creates unbind request)."""
    user_id = get_current_user_id(authorization, db)
    space_info = get_user_couple_space(db, user_id)

    if not space_info:
        raise HTTPException(status_code=400, detail="User not in any couple space")

    # Generate verify code for unbind
    from app.core.security import generate_verify_code
    verify_code = generate_verify_code()
    expires_at = calculate_expiry(hours=24)

    unbind_request = P0UnbindRequest(
        space_id=space_info["spaceId"],
        requested_by=user_id,
        verify_code=verify_code,
        expires_at=expires_at.strftime("%Y-%m-%d %H:%M:%S")
    )
    db.add(unbind_request)
    db.commit()

    return {
        "success": True,
        "verifyCode": verify_code,
        "expiresAt": expires_at.strftime("%Y-%m-%d %H:%M:%S")
    }


@router.get("/members", response_model=dict)
def get_space_members(
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Get all members of the current couple space."""
    user_id = get_current_user_id(authorization, db)
    space_info = get_user_couple_space(db, user_id)

    if not space_info:
        raise HTTPException(status_code=400, detail="User not in any couple space")

    members = db.query(P0CoupleMember).filter(
        P0CoupleMember.space_id == space_info["spaceId"]
    ).all()

    member_list = []
    for m in members:
        user = db.query(P0User).filter(P0User.id == m.user_id).first()
        member_list.append({
            "userId": m.user_id,
            "nickname": m.nickname,
            "role": m.role,
            "avatar": user.avatar if user else None,
            "joinedAt": m.joined_at
        })

    return {
        "members": member_list,
        "count": len(member_list)
    }