from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.services import user_service


def validate_user_email_not_exists(email: str, db: Session) -> None:
    user = user_service.get_filtered_by(db, email=email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already in use",
        )


def validate_user_username_not_exists(username: str, db: Session):
    user = user_service.get_filtered_by(db, username=username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already in use",
        )
