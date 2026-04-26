from djoser.email import ActivationEmail, PasswordResetEmail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from djoser.conf import settings as djoser_settings
from urllib.parse import urlparse


def build_frontend_url(path: str):
    """
    Rebuilds a frontend-only URL for activation and password reset.
    Works even if DJOSER sends a full backend URL.
    """
    parsed = urlparse(path)
    clean_path = parsed.path.lstrip("/")

    parts = clean_path.split("/")

    uid = parts[-2]
    token = parts[-1]

    prefix = "/".join(parts[:-2])

    domain = djoser_settings.DOMAIN

    return f"https://{domain}/{prefix}/{uid}/{token}"


class CustomActivationEmail(ActivationEmail):
    template_name = "email/activation_email.html"

    def get_context_data(self):
        context = super().get_context_data()
        request = getattr(self, "request", None)

        activation_path = context.get("activation_url")

        if activation_path:
            context["url"] = build_frontend_url(activation_path)
        else:
            context["url"] = activation_path

        return context

    def send(self, to, *args, **kwargs):
        context = self.get_context_data()
        url = context.get("url")

        if not url:
            uid = context.get("uid")
            token = context.get("token")
            if uid and token:
                path = djoser_settings.ACTIVATION_URL.format(
                    uid=uid, token=token)
                context["url"] = build_frontend_url(path)
            else:
                raise ValueError("Activation URL is missing in email context.")

        html_content = render_to_string(self.template_name, context)
        text_content = strip_tags(html_content)

        to_addresses = to if isinstance(to, list) else [to]
        subject = "Activate your Online Therapy Account"

        email_message = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            to=to_addresses,
        )
        email_message.attach_alternative(html_content, "text/html")
        email_message.send()


class CustomPasswordResetEmail(PasswordResetEmail):
    template_name = "email/password_reset_email.html"

    def get_context_data(self):
        context = super().get_context_data()
        request = getattr(self, "request", None)

        uid = context.get("uid")
        token = context.get("token")

        if uid and token:
            reset_path = djoser_settings.PASSWORD_RESET_CONFIRM_URL.format(
                uid=uid, token=token
            )
        else:
            reset_path = ""

        context["url"] = build_frontend_url(reset_path)

        return context

    def send(self, to, *args, **kwargs):
        context = self.get_context_data()
        url = context.get("url")

        if not url:
            raise ValueError("Password reset URL is missing in email context.")

        html_content = render_to_string(self.template_name, context)
        text_content = strip_tags(html_content)

        to_addresses = to if isinstance(to, list) else [to]
        subject = "Reset your Online Therapy Password"

        email_message = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            to=to_addresses,
        )
        email_message.attach_alternative(html_content, "text/html")
        email_message.send()


# =========================
# Appointment Notifications
# =========================
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_appointment_email(event_type, appointment):
    #  feature flag
    if not getattr(settings, "NOTIFICATIONS_ENABLED", True):
        return

    patient_email = appointment.patient.email
    therapist_email = appointment.therapist.user.email

    subject = ""
    context = {
        "appointment": appointment
    }

    if event_type == "booked":
        subject = "Appointment Booked"
        template = "email/appointment_booked.html"

    elif event_type == "cancelled":
        subject = "Appointment Cancelled"
        template = "email/appointment_cancelled.html"

    elif event_type == "rescheduled":
        subject = "Appointment Rescheduled"
        template = "email/appointment_rescheduled.html"

    elif event_type == "meeting_link":
        subject = "Meeting Link Ready"
        template = "email/meeting_link_ready.html"

    #  missing event
    elif event_type == "confirmed":
        subject = "Appointment Confirmed"
        template = "email/appointment_confirmed.html"

    else:
        return  # safety

    html_content = render_to_string(template, context)
    text_content = strip_tags(html_content)

    #  unified sending + error handling
    recipients = [patient_email]

    if event_type in ["booked", "cancelled"]:
        recipients.append(therapist_email)

    for email in recipients:
        try:
            msg = EmailMultiAlternatives(
                subject,
                text_content,
                to=[email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except Exception as e:
            logger.error(f"Email send failed for {email}: {e}")