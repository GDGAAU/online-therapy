'''therapy/management/commands/send_appointment_reminders.py
===========================================================
Django management command to send email reminders for upcoming appointments.'''


from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from therapy.models import Appointment
from account.email import send_appointment_email
from django.conf import settings


class Command(BaseCommand):
    help = "Send appointment reminders"

    def handle(self, *args, **kwargs):
        hours = getattr(settings, "REMINDER_HOURS_BEFORE", 24)

        now = timezone.now()
        limit = now + timedelta(hours=hours)

        appointments = Appointment.objects.filter(
            status=Appointment.Status.CONFIRMED,
            scheduled_at__gte=now,
            scheduled_at__lte=limit,
            reminder_sent_at__isnull=True,
        )

        for appt in appointments:
            try:
                send_appointment_email("reminder", appt)

                appt.reminder_sent_at = now
                appt.save(update_fields=["reminder_sent_at"])

                self.stdout.write(f"Sent reminder: {appt.id}")

            except Exception as e:
                self.stderr.write(f"Failed {appt.id}: {str(e)}")