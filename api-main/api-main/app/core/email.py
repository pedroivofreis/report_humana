from pathlib import Path
from typing import Any

import mailtrap as mt
import structlog

from app.core.config import settings

logger = structlog.getLogger(__name__)

_PASSWORD_RESET_TEMPLATE_PATH = (
    Path(__file__).resolve().parent.parent / "templates" / "email" / "password_reset.html"
)


def _render_password_reset_html(reset_link: str) -> str:
    raw = _PASSWORD_RESET_TEMPLATE_PATH.read_text(encoding="utf-8")
    return raw.replace("{{RESET_LINK}}", reset_link)


class EmailService:
    def __init__(self) -> None:
        self.api_key = settings.MAIL_TRAP_API_KEY
        self.inbox_id = settings.MAIL_TRAP_INBOX_ID

        if not self.api_key:
            logger.warning("MAIL_TRAP_API_KEY is not set. Email service disabled.")

    async def send_email(
        self, to_email: str, subject: str, text: str, html: str | None = None
    ) -> dict[str, Any] | None:
        if not self.api_key:
            return {"status": "skipped", "message": "API key missing"}

        client = mt.MailtrapClient(token=self.api_key, sandbox=True, inbox_id=self.inbox_id)

        mail = mt.Mail(
            sender=mt.Address(email="mailtrap@humana.com", name="Humana API"),
            to=[mt.Address(email=to_email)],
            subject=subject,
            text=text,
            category="Password Reset",
            html=html,
        )

        try:
            response = client.send(mail)
            logger.info(f"Email sent to {to_email}")
            return {"status": "success", "response": str(response)}
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            raise

    async def send_password_reset_email(self, to_email: str, token: str) -> None:
        reset_link = f"{settings.RESET_PASSWORD_URL}?token={token}"
        subject = "Humana — Redefinição de senha"
        text = (
            "Olá,\n\n"
            "Recebemos um pedido para redefinir a senha da sua conta Humana.\n\n"
            "Abra o link abaixo no navegador (válido por cerca de 1 hora):\n"
            f"{reset_link}\n\n"
            "Se você não solicitou, ignore este e-mail.\n\n"
            "— Equipe Humana"
        )
        html = _render_password_reset_html(reset_link)
        await self.send_email(to_email, subject, text, html)
