from celery import shared_task
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task
def notify_doctor_email(doctor_email, doctor_name, patient_name):
    # Debug: Print settings that Celery sees
    logger.info("=== CELERY EMAIL DEBUG ===")
    logger.info(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'NOT SET')}")
    logger.info(f"DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'NOT SET')}")
    logger.info(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'NOT SET')}")
    logger.info(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'NOT SET')}")
    logger.info(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'NOT SET')}")
    logger.info(f"EMAIL_HOST_PASSWORD length: {len(getattr(settings, 'EMAIL_HOST_PASSWORD', ''))}")

    try:
        subject = f'New Patient Assigned: {patient_name}'
        message = f'''Dear Dr. {doctor_name},

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
            logger.info("✅ SMTP connection successful in Celery")
            connection.close()
        except Exception as conn_e:
            logger.error(f"❌ SMTP connection failed in Celery: {conn_e}")
            raise conn_e

        # Send email using send_mail with explicit from_email
        result = send_mail(
            subject=subject,
            message=message,
            from_email='blessyvarghese0326@gmail.com',  # Explicit email
            recipient_list=['blessyvarghese0326@gmail.com'],
            fail_silently=False,
        )

        if result == 1:
            logger.info(f"✅ Email sent successfully to {doctor_email}")
            return f"Email sent successfully to {doctor_email}"
        else:
            logger.error(f"❌ Email sending failed - send_mail returned: {result}")
            return f"Email sending failed to {doctor_email}"

    except Exception as e:
        logger.error(f"❌ Failed to send email to {doctor_email}: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        # Re-raise to trigger Celery retry if needed
        raise e


@shared_task
def notify_doctor_email_html(doctor_email, doctor_name, patient_name):
    """Alternative task with HTML email support"""
    try:
        subject = f'New Patient Assigned: {patient_name}'

        # Plain text message
        plain_message = f'''Dear Dr. {doctor_name},

You have been assigned to a new patient: {patient_name}.

Please log in to the Health Record System to view the patient's records and provide necessary care.

Best regards,
Health Record System Team
'''

        # HTML message
        html_message = f'''
        <html>
        <body>
            <h2>New Patient Assignment</h2>
            <p>Dear Dr. {doctor_name},</p>
            <p>You have been assigned to a new patient: <strong>{patient_name}</strong>.</p>
            <p>Please log in to the Health Record System to view the patient's records and provide necessary care.</p>
            <br>
            <p>Best regards,<br>
            <strong>Health Record System Team</strong></p>
        </body>
        </html>
        '''

        # Create EmailMessage for more control
        email = EmailMessage(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[doctor_email],
        )

        # Add HTML alternative
        email.attach_alternative(html_message, "text/html")

        # Send email
        result = email.send(fail_silently=False)

        if result == 1:
            logger.info(f"HTML email sent successfully to {doctor_email}")
            return f"HTML Email sent successfully to {doctor_email}"
        else:
            logger.error(f"HTML email sending failed - send returned: {result}")
            return f"HTML Email sending failed to {doctor_email}"

    except Exception as e:
        logger.error(f"Failed to send HTML email to {doctor_email}: {str(e)}")
        raise e


@shared_task
def test_email_task():
    """Test task to verify email configuration"""
    try:
        result = send_mail(
            subject='Test Email from Health Record System',
            message='This is a test email to verify email configuration is working.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['blessyvarghese0326@gmail.com'],
            fail_silently=False,
        )

        if result == 1:
            logger.info("Test email sent successfully")
            return "Test email sent successfully"
        else:
            logger.error(f"Test email failed - send_mail returned: {result}")
            return "Test email failed"

    except Exception as e:
        logger.error(f"Test email error: {str(e)}")
        raise e