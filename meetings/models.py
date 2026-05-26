import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Meeting(models.Model):
    host         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_meetings')
    meeting_id   = models.CharField(max_length=20, unique=True, blank=True)
    title        = models.CharField(max_length=200)
    description  = models.TextField(blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    is_active    = models.BooleanField(default=True)
    participants = models.ManyToManyField(User, related_name='joined_meetings', blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.meeting_id:
            raw = str(uuid.uuid4()).replace('-', '').upper()
            self.meeting_id = f"{raw[:3]}-{raw[3:7]}-{raw[7:10]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.meeting_id})"

    def is_scheduled(self):
        return self.scheduled_at is not None

    def is_upcoming(self):
        if self.scheduled_at:
            return self.scheduled_at > timezone.now()
        return False

    def participant_count(self):
        return self.participants.count()