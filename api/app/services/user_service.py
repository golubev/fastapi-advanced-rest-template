from sqlalchemy.orm import Session
from sqlalchemy.sql import exists

from app.core.security import get_password_hash, verify_password
from app.models import User
from app.schemas.user import UserCreate, UserUpdate

from .base_service import BaseService
from .exceptions import UniqueConstraintViolationException


class UserService(BaseService[User]):
    def get(self, db: Session, id: int) -> User | None:
        return self._get(db, id)

    def get_or_exception(self, db: Session, id: int) -> User:
        """
        Get a User by id. Raise exception if not found.
        """
        return self._get_or_exception(db, id)

    def get_by_username(self, db: Session, username: str) -> User | None:
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

    def create(self, db: Session, create_api_model: UserCreate) -> User:
        self._validate_email_unique(db, create_api_model.email)
        self._validate_username_unique(db, create_api_model.username)
        data_to_create_prepared = dict(
            **create_api_model.dict(exclude={"password"}),
            hashed_password=get_password_hash(
                create_api_model.password.get_secret_value()
            ),
        )
        return self._create(db, data_to_create_prepared)

    def update(
        self,
        db: Session,
        db_model: User,
        update_api_model: UserUpdate,
    ) -> None:
        if update_api_model.username != db_model.username:
            self._validate_username_unique(db, update_api_model.username)
        data_to_update_prepared = update_api_model.dict()
        self._update(db, db_model, data_to_update_prepared)

    def delete(self, db: Session, db_model: User) -> None:
        self._delete(db, db_model)

    def _validate_email_unique(self, db: Session, email: str) -> None:
        if db.query(exists().where(User.email == email)).scalar():
            raise UniqueConstraintViolationException("Email already in use")

    def _validate_username_unique(self, db: Session, username: str) -> None:
        if db.query(exists().where(User.username == username)).scalar():
            raise UniqueConstraintViolationException("Username already in use")


user_service = UserService(User)
