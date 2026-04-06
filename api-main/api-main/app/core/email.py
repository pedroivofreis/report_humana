from typing import Any

import mailtrap as mt
import structlog

from app.core.config import settings

logger = structlog.getLogger(__name__)


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
        subject = "Password Reset Request"
        text = f"You requested a password reset. Click the following link to reset your password: {reset_link}"
        html = f"""
        <html>
            <body>
                <h1>Password Reset Request</h1>
                <p>You requested a password reset. Click the following link to reset your password:</p>
                <p><a href="{reset_link}">Reset Password</a></p>
                <p>If you did not request this, please ignore this email.</p>
            </body>
        </html>
        """
        await self.send_email(to_email, subject, text, html)
