# blog/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Blog, Reaction, Comment
from django.db.models import Q
from .forms import BlogSearchForm

def blog_list(request):
    category = request.GET.get('category')
    posts = Blog.objects.filter(published=True).order_by('-created_at')
    
    if category:
        # Validate category against our choices
        valid_categories = [choice[0] for choice in Blog.CATEGORY_CHOICES]
        if category in valid_categories:
            posts = posts.filter(category=category)
    
    return render(request, 'blog/blog_list.html', {
        'posts': posts,
        'categories': dict(Blog.CATEGORY_CHOICES),  # Pass categories for navigation
        'current_category': category  # Pass current category for UI highlighting
    })

def blog_detail(request, slug):
    post = get_object_or_404(Blog, slug=slug, published=True)
    post.views += 1
    post.save(update_fields=['views'])
    return render(request, 'blog/blog_detail.html', {'post': post})

def blog_search(request):
    form = BlogSearchForm(request.GET or None)
    posts = Blog.objects.filter(published=True).order_by('-created_at')
    
    if form.is_valid():
        query = form.cleaned_data.get('q')
        category = form.cleaned_data.get('category')
        
        if query:
            posts = posts.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(tags__name__icontains=query) |
                Q(category__icontains=query)
            ).distinct()
        
        if category:
            posts = posts.filter(category=category)
    
    return render(request, 'blog/blog_list.html', {
        'posts': posts,
        'categories': dict(Blog.CATEGORY_CHOICES),
        'search_form': form,
        'search_query': request.GET.get('q', ''),
        'current_category': request.GET.get('category')
    })   

@require_POST
def add_reaction(request, post_id):
    blog_post = get_object_or_404(Blog, id=post_id)
    reaction_type = request.POST.get('reaction')
    
    if not reaction_type:
        return JsonResponse({'status': 'error', 'message': 'Reaction type required'}, status=400)
    
    # Check if user already has this reaction
    existing_reaction = Reaction.objects.filter(
        user=request.user,
        blog=blog_post,
        type=reaction_type
    ).first()
    
    if existing_reaction:
        existing_reaction.delete()  # Toggle reaction off
        action = 'removed'
    else:
        # Remove any existing reaction of different type
        Reaction.objects.filter(user=request.user, blog=blog_post).delete()
        # Add new reaction
        Reaction.objects.create(
            user=request.user,
            blog=blog_post,
            type=reaction_type
        )
        action = 'added'
    
    # Return updated reaction counts
    reaction_counts = {
        'like': blog_post.reactions.filter(type='like').count(),
        'love': blog_post.reactions.filter(type='love').count(),
        'clap': blog_post.reactions.filter(type='clap').count(),
        'insightful': blog_post.reactions.filter(type='insightful').count(),
        'laugh': blog_post.reactions.filter(type='laugh').count(),
    }
    
    return JsonResponse({
        'status': 'success',
        'action': action,
        'reaction': reaction_type,
        'reaction_html': render_to_string('blog/reaction_counts.html', {
            'post': blog_post,
            'user': request.user
        }),
        'reaction_counts': reaction_counts
    })

@require_POST
@login_required
def add_comment(request, post_id):
    blog_post = get_object_or_404(Blog, id=post_id)
    content = request.POST.get('content', '').strip()
    
    if not content:
        return JsonResponse({'status': 'error', 'message': 'Comment cannot be empty'}, status=400)
    
    comment = Comment.objects.create(
        blog=blog_post,
        user=request.user,
        content=content
    )
    
    return JsonResponse({
        'status': 'success',
        'comments_html': render_to_string('blog/comments.html', {
            'post': blog_post,
            'user': request.user
        })
    })

@require_POST
@login_required
def add_reply(request, comment_id):
    parent_comment = get_object_or_404(Comment, id=comment_id)
    content = request.POST.get('content', '').strip()
    
    if not content:
        return JsonResponse({'status': 'error', 'message': 'Reply cannot be empty'}, status=400)
    
    reply = Comment.objects.create(
        blog=parent_comment.blog,
        user=request.user,
        content=content,
        parent=parent_comment
    )
    
    return JsonResponse({
        'status': 'success',
        'replies_html': render_to_string('blog/replies.html', {
            'replies': parent_comment.replies.all()
        })
    })