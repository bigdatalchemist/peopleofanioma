# blog/models.py
from django.db import models
from django.utils.text import slugify
from storages.backends.s3boto3 import S3Boto3Storage
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()

class Author(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField()
    photo = models.ImageField(upload_to='authors/', blank=True, null=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Blog(models.Model):
    CATEGORY_CHOICES = [
        ('history', 'History'),
        ('events', 'Events'),
        ('lifestyle', 'Lifestyle'),
        ('tradition', 'Tradition'),
        ('culture', 'Culture'),
        ('entertainment', 'Entertainment'),
        ('news', 'News'),
        ('business', 'Business'),
        ('literature', 'Literature'),
        ('technology', 'Technology'),
        ('sports', 'Sports'),
        ('spotlight', 'Spotlight'),
    ]
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='news'
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Handle potential slug duplicates
            counter = 1
            while Blog.objects.filter(slug=self.slug).exists():
                self.slug = f"{slugify(self.title)}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Reaction(models.Model):
    REACTION_CHOICES = [
        ('like', '👍 Like'),
        ('love', '❤️ Love'),
        ('clap', '👏 Clap'),
        ('insightful', '💡 Insightful'),
        ('laugh', '😂 Laugh'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_reactions')
    blog = models.ForeignKey(Blog, related_name='reactions', on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'blog', 'type')

    def __str__(self):
        return f"{self.user.username} reacted {self.get_type_display()} to {self.blog.title}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_comments')
    blog = models.ForeignKey(Blog, related_name='comments', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        
    @property
    def is_reply(self):
        return self.parent is not None

    def __str__(self):
        return f"Comment by {self.user.username} on {self.blog.title}"

class VideoCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True)

    class Meta:
        verbose_name = "Video Category"
        verbose_name_plural = "Video Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


def video_upload_path(instance, filename):
    return f"videos/{instance.slug}/{filename}"

class VideoPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        VideoCategory, related_name="videos", on_delete=models.SET_NULL, null=True, blank=True
    )

    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_videos"
    )
    # Either upload a file OR use an external embed URL (YouTube/Vimeo/etc.)
    video_file = models.URLField(blank=True, null=True, help_text="S3 or external video URL (YouTube, Vimeo, etc.)")
    external_url = models.URLField(blank=True)  # e.g. https://youtu.be/..., https://vimeo.com/...
    thumbnail = models.ImageField(upload_to="videos/thumbnails/", blank=True, null=True)

    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)
    views = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title
    
    def clean(self):
        from django.core.exceptions import ValidationError

        if self.video_file and self.external_url:
            raise ValidationError(
                "Provide either a video URL or an external embed URL, not both."
            )

        if not self.video_file and not self.external_url:
            raise ValidationError(
                "You must provide either a video URL or an external embed URL."
            )

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:200]
            candidate = base
            i = 1
            while VideoPost.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                i += 1
                candidate = f"{base}-{i}"
            self.slug = candidate
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:video_detail", args=[self.slug])

    @property
    def is_external(self):
        return bool(self.external_url) and not self.video_file

    @property
    def player_source(self):
        """Return the src/iframe info the template should use."""
        if self.is_external:
            return self.external_url
        return self.video_file or ""
