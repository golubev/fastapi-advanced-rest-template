from app.models import User


def make_user_create_dict(
    db_model: User,
    *,
    password: str,
) -> dict[str, str | None]:
    return {
        "username": db_model.username,
        "full_name": db_model.full_name,
        "email": db_model.email,
        "password": password,
    }


def make_user_response_dict(db_model: User) -> dict[str, str | int | None]:
    return {
        "id": db_model.id,
        "username": db_model.username,
        "full_name": db_model.full_name,
        "email": db_model.email,
    }
