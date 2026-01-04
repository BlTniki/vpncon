import smtplib
import threading
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .config import Config

logger = logging.getLogger(__name__)

class SMTPNotifier:
    def __init__(self):
        self.enabled = Config.EMAIL_NOTIFIER_ENABLED
        self.name = Config.EMAIL_NOTIFIER_NAME
        self.smtp_server = Config.EMAIL_SMTP_SERVER
        self.smtp_port = Config.EMAIL_SMTP_PORT
        self.smtp_user = Config.EMAIL_USER
        self.smtp_pass = Config.EMAIL_PASS
        self.email_to = Config.EMAIL_TO

    def send_email(self, subject:str, body:str):
        if not self.enabled:
            logger.info("SMTP Notifier is disabled, skipping email send")
            return
        if not all([self.smtp_server, self.smtp_user, self.smtp_pass, self.email_to]):
            logger.warning("SMTP configuration incomplete, skipping email send")
            return

        msg = MIMEMultipart()
        msg['From'] = self.name + " <" + self.smtp_user + ">"
        msg['To'] = self.email_to
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP(self.smtp_server, port=self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            logger.info("Email sent successfully")
        except Exception as e:
            logger.error("Failed to send email: %s", e)

    def notify(self, subject:str, body:str):
        # Отправка в отдельном потоке, чтобы не блокировать
        thread = threading.Thread(target=self.send_email, args=(subject, body))
        thread.daemon = True
        thread.start()

# Глобальный экземпляр
smtp_notifier = SMTPNotifier()

def notify(subject:str, body:str):
    """Отправить уведомление по SMTP на почту, заданный в EMAIL_TO конфига
    """
    logger.info("Sending SMTP notification: {%s, %s}", subject, body)
    smtp_notifier.notify(subject, body)