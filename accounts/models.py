from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar     = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio        = models.TextField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None