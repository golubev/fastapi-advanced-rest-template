from typing import Any

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.base_service import BaseService


class UserService(BaseService[User, UserCreate, UserUpdate]):
    def get_filtered_by(
        self, db: Session, *, email: str | None = None, username: str | None = None
    ) -> User | None:
        query = db.query(User)
        if email is not None:
            query = query.filter(User.email == email)
        if username is not None:
            query = query.filter(User.username == username)
        return query.first()

    def get_by_credentials_verified(
        self, db: Session, *, username: str, password: str
    ) -> User | None:
        user = self.get_filtered_by(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def create(self, db: Session, data_to_create: UserCreate | dict[str, Any]) -> User:
        if isinstance(data_to_create, dict):
            data_to_create = UserCreate(**data_to_create)
        data_to_create_prepared = dict(
            username=data_to_create.username,
            email=data_to_create.email,
            full_name=data_to_create.full_name,
            hashed_password=get_password_hash(
                data_to_create.password.get_secret_value()
            ),
        )
        return super().create(db, data_to_create_prepared)


user_service = UserService(User)
