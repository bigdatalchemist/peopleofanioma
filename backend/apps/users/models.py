# apps.users.models.py
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    # Add your custom fields below
    bio = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', 
                                        blank=True, 
                                        null=True, 
                                        verbose_name='Profile Picture')
    @property
    def profile_picture_url(self):
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return '/static/images/default-profile.png'

    def approved_stories(self):
        return self.stories.filter(is_approved=True)
    
    def diaspora_entries(self):
        from apps.diaspora_tracker.models import DiasporaEntry  # Local import to avoid circularity
        return DiasporaEntry.objects.filter(name=self)

    def __str__(self):
        return self.username
