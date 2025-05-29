from celery import shared_task
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task
def notify_doctor_email(doctor_email, doctor_name, patient_name):
    try:
        subject = f'New Patient Assigned: {patient_name}'
        message = f'''Dear {doctor_name},

You have been assigned to a new patient: {patient_name}.

Please log in to the Health Record System to view the patient's records and provide necessary care.

Best regards,
Health Record System Team
'''

        # Log the attempt
        logger.info(f"Attempting to send email to: {doctor_email}")
        logger.info(f"From email: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'NOT SET')}")
        logger.info(f"Subject: {subject}")

        # Test SMTP connection first
        from django.core.mail import get_connection
        connection = get_connection()
        try:
            connection.open()
            logger.info("SMTP connection successful in Celery")
            connection.close()
        except Exception as conn_e:
            logger.error(f"SMTP connection failed in Celery: {conn_e}")
            raise conn_e

        # Send email using send_mail with explicit from_email
        result = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,  # Explicit email
            recipient_list=[doctor_email],
            fail_silently=False,
        )

        if result == 1:
            logger.info(f" Email sent successfully to {doctor_email}")
            return f"Email sent successfully to {doctor_email}"
        else:
            logger.error(f" Email sending failed - send_mail returned: {result}")
            return f"Email sending failed to {doctor_email}"

    except Exception as e:
        logger.error(f" Failed to send email to {doctor_email}: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        # Re-raise to trigger Celery retry if needed
        raise e
