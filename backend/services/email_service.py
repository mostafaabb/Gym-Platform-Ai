import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, Optional

from backend.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def send_email(
        email_to: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email using SMTP settings.
        If SMTP settings are missing, it logs the email content instead.
        """
        # Validate settings
        if not all([settings.SMTP_HOST, settings.SMTP_PORT, settings.SMTP_USER, settings.SMTP_PASSWORD]):
            logger.warning(f"SMTP settings not fully configured. MOCKING EMAIL TO: {email_to}")
            logger.info(f"--- MOCK EMAIL START ---")
            logger.info(f"TO: {email_to}")
            logger.info(f"SUBJECT: {subject}")
            logger.info(f"CONTENT (Preview): {html_content[:200]}...")
            logger.info(f"--- MOCK EMAIL END ---")
            return True

        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = settings.EMAILS_FROM_EMAIL
            message["To"] = email_to

            # Add text version if provided
            if text_content:
                part1 = MIMEText(text_content, "plain")
                message.attach(part1)

            # Add HTML version
            part2 = MIMEText(html_content, "html")
            message.attach(part2)

            # Connect and send
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.EMAILS_FROM_EMAIL, email_to, message.as_string())
            
            logger.info(f"Email sent successfully to {email_to}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {email_to}: {str(e)}")
            return False

    @staticmethod
    def send_password_reset_email(email_to: str, token: str) -> bool:
        """Send a password reset email with the verification token."""
        # In a real app, this URL should point to your frontend
        # The frontend URL can be passed via settings or constructed
        frontend_url = "https://gymflow-frontend-4izm.onrender.com"
        reset_url = f"{frontend_url}/auth/reset-password?token={token}&email={email_to}"
        
        subject = "Reset Your GymFlow AI Password"
        
        # Premium HTML Template
        html_content = f"""
        <html>
            <body style="font-family: 'Inter', sans-serif; background-color: #000; color: #fff; padding: 40px; margin: 0;">
                <div style="max-width: 600px; margin: 0 auto; background: #0a0a0a; border: 1px solid #1a1a1a; border-radius: 24px; padding: 40px; text-align: center;">
                    <div style="margin-bottom: 30px;">
                        <h1 style="color: #00ff88; margin: 0; font-size: 32px; letter-spacing: -1px;">GYMFLOW AI</h1>
                    </div>
                    <h2 style="font-size: 24px; font-weight: 700; margin-bottom: 20px;">Reset Your Password</h2>
                    <p style="color: #a1a1aa; font-size: 16px; line-height: 1.6; margin-bottom: 30px;">
                        We received a request to reset your password. Use the verification code below or click the button to continue.
                    </p>
                    
                    <div style="background: #1a1a1a; padding: 20px; border-radius: 16px; margin-bottom: 30px;">
                        <span style="font-family: monospace; font-size: 32px; letter-spacing: 4px; color: #00ff88; font-weight: 700;">
                            {token}
                        </span>
                    </div>
                    
                    <a href="{reset_url}" style="display: inline-block; background: #00ff88; color: #000; padding: 16px 32px; border-radius: 14px; font-weight: 700; text-decoration: none; margin-bottom: 30px;">
                        Reset Password Now
                    </a>
                    
                    <p style="color: #71717a; font-size: 14px; line-height: 1.5;">
                        This code will expire in 24 hours. If you didn't request this, you can safely ignore this email.
                    </p>
                    
                    <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #1a1a1a;">
                        <p style="color: #52525b; font-size: 12px;">
                            © 2026 GymFlow AI. Precision Training for the Elite.
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        text_content = f"Reset your GymFlow AI password. Your verification code is: {token}. Link: {reset_url}"
        
        return EmailService.send_email(email_to, subject, html_content, text_content)
