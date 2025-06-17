# apps/dashboards/views.py
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from apps.blog.models import Blog
from apps.stories.models import Story

def dashboard_view(request):
    # Get categories from Blog model
    categories = dict(Blog.CATEGORY_CHOICES)
    
    # Get date range for recent content (30 days)
    recent_days = timezone.now() - timedelta(days=30)
    
    # Get top blog posts (fallback to recent if no popular ones)
    top_blog_posts = Blog.objects.filter(
        published=True,
        created_at__gte=recent_days
    ).order_by('-views', '-created_at')[:4]
    
    if not top_blog_posts.exists():
        top_blog_posts = Blog.objects.filter(
            published=True
        ).order_by('-created_at')[:4]
    
    # Get top stories - using is_approved instead of published
    top_stories = Story.objects.filter(
        is_approved=True  # Using the correct field name
    ).order_by('-upvotes')[:3]
    
    # Get current category from request
    current_category = request.GET.get('category')
    
    # Validate category exists
    if current_category and current_category not in categories:
        current_category = None
    
    return render(request, 'dashboards/dashboard.html', {
        'categories': categories,
        'current_category': current_category,
        'top_blog_posts': top_blog_posts,
        'top_stories': top_stories,
    })