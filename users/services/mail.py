# users/services/mail.py
import logging
import mailtrap as mt
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail as django_send_mail

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.is_local = settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend'
        if not self.is_local:
            self.client = mt.MailtrapClient(token=settings.MAILTRAP_API_TOKEN)
            self.sender = mt.Address(
                email=settings.MAILTRAP_SENDER_EMAIL,
                name="MyBlueList"
            )

    def send_email(self, to_email, subject, html_content, text_content=None):
        """
        Send an email using either Mailtrap API or console backend
        """
        try:
            if text_content is None:
                text_content = strip_tags(html_content)

            if self.is_local:
                # Use Django's send_mail for local development
                django_send_mail(
                    subject=subject,
                    message=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[to_email],
                    html_message=html_content
                )
                logger.info(f"[LOCAL] Email would be sent to {to_email}")
                return True, None
            else:
                # Use Mailtrap for production
                mail = mt.Mail(
                    sender=self.sender,
                    to=[mt.Address(email=to_email)],
                    subject=subject,
                    html=html_content,
                    text=text_content
                )
                response = self.client.send(mail)
                logger.info(f"Email sent successfully to {to_email}.")
                return True, None

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}", exc_info=True)
            return False, None

    def send_verification_email(self, user, verification_url):
        """
        Send account verification email
        """
        subject = "Verify your MyBlueList account"
        
        context = {
            'user': user,
            'verification_url': verification_url
        }
        
        html_content = render_to_string('users/emails/verification_email.html', context)
        text_content = render_to_string('users/emails/verification_email.txt', context)
        
        return self.send_email(user.email, subject, html_content, text_content)