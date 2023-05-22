from src.core.email import compose_email
from src.models import User


def compose_registration_email(user: User) -> tuple[str, str]:
    return compose_email(
        "Welcome onboard, {{ user.username }}!",
        "user_registered.html",
        {
            "user": user,
        },
    )
