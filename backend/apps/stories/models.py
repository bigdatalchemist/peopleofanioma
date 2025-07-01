# stories/models.py
from django.db import models
from django.utils.text import slugify
from django.conf import settings
import os
from django.core.files.base import ContentFile
from pydub import AudioSegment
from io import BytesIO
import itertools
from storages.backends.s3boto3 import S3Boto3Storage



class Story(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stories')
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    author_name = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(upload_to='story_images/', blank=True, null=True)
    audio = models.FileField(upload_to='story_audio/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    date_submitted = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = base_slug
            for i in itertools.count(1):
                if not Story.objects.filter(slug=self.slug).exists():
                    break
                self.slug = f"{base_slug}-{i}"

        if self.audio and self.audio.name.endswith('.webm'):
            self.audio.seek(0)
            AudioSegment.converter = "C:/ffmpeg/bin/ffmpeg.exe"
            sound = AudioSegment.from_file(self.audio, format='webm')

            mp3_io = BytesIO()
            sound.export(mp3_io, format='mp3')
            mp3_file = ContentFile(mp3_io.getvalue(), name=os.path.splitext(self.audio.name)[0] + '.mp3')
            self.audio = mp3_file

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} by {self.author_name}"
    
    @property
    def reaction_counts(self):
        """Alternative counting method that's consistent with the template filter approach"""
        return {
            'like': self.reactions.filter(type='like').count(),
            'love': self.reactions.filter(type='love').count(),
            'clap': self.reactions.filter(type='clap').count(),
            'insightful': self.reactions.filter(type='insightful').count(),
            'laugh': self.reactions.filter(type='laugh').count(),
        }
    
    def get_user_reaction(self, user):
        """Get the current user's reaction type if exists"""
        if user.is_authenticated:
            reaction = self.reactions.filter(user=user).first()
            return reaction.type if reaction else None
        return None
    
class StoryReaction(models.Model):
    REACTION_CHOICES = [
        ('like', '👍 Like'),
        ('love', '❤️ Love'),
        ('clap', '👏 Clap'),
        ('insightful', '💡 Insightful'),
        ('laugh', '😂 Laugh'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='story_reactions')
    story = models.ForeignKey('Story', related_name='reactions', on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'story', 'type')  # One reaction per user per story
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} reacted {self.get_type_display()} to {self.story.title}"


class Comment(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.story.title}"


from django import forms

class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        exclude = ['user', 'is_approved', 'slug', 'date_submitted']
