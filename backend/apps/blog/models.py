# blog/models.py
from django.db import models
from django.utils.text import slugify
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