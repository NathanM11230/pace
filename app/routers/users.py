import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse, UserUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    """Create a new user account."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A user with email '{payload.email}' already exists.",
        )

    user = User(
        email=payload.email,
        name=payload.name,
        interests=payload.interests,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("Created user id=%d email=%s", user.id, user.email)
    return user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Retrieve a user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found.",
        )
    return user


@router.put("/{user_id}/interests", response_model=UserResponse)
def update_interests(
    user_id: int, payload: UserUpdate, db: Session = Depends(get_db)
):
    """Replace a user's interest categories."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found.",
        )
    user.interests = payload.interests
    db.commit()
    db.refresh(user)
    logger.info("Updated interests for user id=%d: %s", user.id, user.interests)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Permanently delete a user and their interaction history."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found.",
        )
    db.delete(user)
    db.commit()
    logger.info("Deleted user id=%d", user_id)
