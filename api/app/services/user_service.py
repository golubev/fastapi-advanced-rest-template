from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy.sql import exists

from app.core.security import get_password_hash, verify_password
from app.models import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.base_service import BaseService
from app.services.exceptions import UniqueConstraintViolationException


class UserService(BaseService[User, UserCreate, UserUpdate]):
    def get_by_username(self, db: Session, username: str) -> User | None:
        """
        Get users filter by fields' values passed in the keyword arguments.
        """
        return db.query(User).filter(User.username == username).first()

    def get_by_credentials_verified(
        self, db: Session, *, username: str, password: str
    ) -> User | None:
        """
        Get a user by his login credentials with password verification.
        """
        user = self.get_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def create(self, db: Session, data_to_create: UserCreate | dict[str, Any]) -> User:
        """
        Create a new user.
        """
        if isinstance(data_to_create, dict):
            data_to_create = UserCreate(**data_to_create)
        self._validate_email_unique(db, data_to_create.email)
        self._validate_username_unique(db, data_to_create.username)
        data_to_create_prepared = dict(
            **data_to_create.dict(exclude={"password"}),
            hashed_password=get_password_hash(
                data_to_create.password.get_secret_value()
            ),
        )
        return super().create(db, data_to_create_prepared)

    def update(
        self,
        db: Session,
        db_model: User,
        data_to_update: UserUpdate | dict[str, Any],
    ) -> None:
        """
        Update a user.
        """
        if isinstance(data_to_update, dict):
            data_to_update = UserUpdate(**data_to_update)
        if data_to_update.username != db_model.username:
            self._validate_username_unique(db, data_to_update.username)
        return super().update(db, db_model, data_to_update)

    def _validate_email_unique(self, db: Session, email: str) -> None:
        if db.query(exists().where(User.email == email)).scalar():
            raise UniqueConstraintViolationException("Email already in use")

    def _validate_username_unique(self, db: Session, username: str) -> None:
        if db.query(exists().where(User.username == username)).scalar():
            raise UniqueConstraintViolationException("Username already in use")


user_service = UserService(User)
