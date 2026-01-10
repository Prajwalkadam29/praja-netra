import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    def send_department_alert(self, recipient_email: str, complaint_details: dict):
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.warning("SMTP credentials not configured. Skipping email.")
            return

        msg = MIMEMultipart()
        msg['From'] = settings.MAIL_FROM
        msg['To'] = recipient_email
        msg['Subject'] = f"🚨 URGENT: New Complaint Assigned - {complaint_details['id']}"

        body = f"""
        <h2>Prajā-Netra Government Alert</h2>
        <p>A new grievance has been automatically routed to your department by the AI Intelligence Engine.</p>
        <hr>
        <b>Complaint ID:</b> {complaint_details['id']}<br>
        <b>Title:</b> {complaint_details['title']}<br>
        <b>Severity Score:</b> {complaint_details['severity']}/10<br>
        <b>Location:</b> {complaint_details['location']}<br>
        <hr>
        <p><b>AI Summary:</b> {complaint_details['summary']}</p>
        <p><b>Blockchain TX:</b> {complaint_details['blockchain_hash']}</p>
        <hr>
        <p><i>This is an automated high-integrity alert. Please log in to the official portal to begin investigation.</i></p>
        """

        msg.attach(MIMEText(body, 'html'))

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
                logger.info(f"📧 Notification sent to {recipient_email} for ID {complaint_details['id']}")
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")


notification_service = NotificationService()