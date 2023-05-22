from typing import Any

import emails
from emails.template import JinjaTemplate
from src.config import application_config

# mypy: ignore-errors


def compose_email(
    subject_template: str, body_template_filename: str, render_kwargs: dict[str, Any]
) -> tuple[str, str]:
    subject = _render_from_template(subject_template, **render_kwargs)
    body_html = _render_from_file(body_template_filename, **render_kwargs)

    return (subject, body_html)


def send_email(email_to: str, subject: str, body_html: str) -> None:
    smtp_options = {
        "host": application_config.SMTP_HOST,
        "port": application_config.SMTP_PORT,
    }
    if application_config.SMTP_DO_USE_TLS:
        smtp_options["tls"] = True
    if application_config.SMTP_USER:
        smtp_options["user"] = application_config.SMTP_USER
    if application_config.SMTP_PASSWORD:
        smtp_options["password"] = application_config.SMTP_PASSWORD

    emails.Message(
        mail_to=email_to,
        subject=subject,
        html=body_html,
        mail_from=(
            application_config.EMAIL_FROM_NAME,
            application_config.EMAIL_FROM_EMAIL,
        ),
    ).send(smtp=smtp_options)


def _render_from_template(template: str, **kwargs: Any) -> str:
    return JinjaTemplate(template).render(**kwargs)


def _render_from_file(template_filename: str, **kwargs: Any) -> str:
    with open(
        application_config.EMAIL_TEMPLATES_DIR + template_filename
    ) as template_file:
        template_str = template_file.read()
    return _render_from_template(template_str, **kwargs)
