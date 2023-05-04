from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserChangePassword, UserCreate, UserRead, UserUpdate
from app.services.base_service import BaseService


class UserService(BaseService[User, UserCreate, UserRead, UserUpdate]):
    def create(self, db: Session, *, create_api_model: UserCreate) -> UserRead:
        data_to_create = dict(
            username=create_api_model.username,
            email=create_api_model.email,
            full_name=create_api_model.full_name,
            hashed_password=get_password_hash(
                create_api_model.password.get_secret_value()
            ),
        )
        return super().create(db, data_to_create=data_to_create)

    def change_password(
        self, db: Session, *, db_model: User, update_api_model: UserChangePassword
    ) -> UserRead:
        data_to_update = dict(
            hashed_password=get_password_hash(update_api_model.password)
        )
        return super().update(db, db_model=db_model, data_to_update=data_to_update)

    def get_db_model_filtered_by(
        self, db: Session, *, email: str | None = None, username: str | None = None
    ) -> User | None:
        query = db.query(User)
        if email is not None:
            query = query.filter(User.email == email)
        if username is not None:
            query = query.filter(User.username == username)
        return query.first()

    def get_db_model_by_credentials_verified(
        self, db: Session, *, username: str, password: str
    ) -> User | None:
        user = self.get_db_model_filtered_by(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


user_service = UserService(User, UserRead)
