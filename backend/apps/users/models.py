# apps.users.models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from storages.backends.s3boto3 import S3Boto3Storage
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import logging
logger = logging.getLogger(__name__)

class CustomUser(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        related_name="customuser_set",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_set",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

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
    
    
    def delete_profile_pic(self):
        """Safely removes profile picture while keeping the user.
        
        Handles cases where:
        - File deletion might fail (permissions, missing file)
        - Database save might fail
        - Either operation can fail independently
        
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        if not self.profile_picture:
            return True  # Nothing to do, consider this successful

        old_picture = self.profile_picture
        success = False

        try:
            # Delete the file from storage first
            try:
                self.profile_picture.delete(save=False)
            except Exception as file_error:
                logger.warning(
                    "Failed to delete profile picture file for user %s. "
                    "Error: %s - Continuing to clear reference",
                    self.pk,
                    str(file_error)
                )

            # Clear the field reference regardless of file deletion success
            self.profile_picture = None

            # Save the model
            try:
                self.save(update_fields=['profile_picture'])
                success = True
            except Exception as save_error:
                # Revert the picture reference if save fails
                self.profile_picture = old_picture
                logger.error(
                    "Failed to save user %s after profile picture removal. "
                    "Error: %s",
                    self.pk,
                    str(save_error)
                )
                success = False

        except Exception as e:
            logger.exception("Unexpected error during profile picture deletion")
            success = False

        return success

    def approved_stories(self):
        return self.stories.filter(is_approved=True)
    
    def diaspora_entries(self):
        from apps.diaspora_tracker.models import DiasporaEntry  # Local import to avoid circularity
        return DiasporaEntry.objects.filter(name=self)

    def __str__(self):
        return self.username
    
@receiver(pre_delete, sender=CustomUser)
def delete_profile_picture_files(sender, instance, **kwargs):
    """Automatically delete profile picture files when user is deleted"""
    if instance.profile_picture:
        instance.profile_picture.delete(save=False)
