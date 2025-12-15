# blog/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Blog, Reaction, Comment, VideoPost, VideoCategory
from django.db.models import Q, F
from .forms import BlogSearchForm
from django.core.paginator import Paginator


def get_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key

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
    Blog.objects.filter(pk=post.pk).update(views=F('views') + 1)
    post.refresh_from_db(fields=['views'])
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

    session_key = get_session_key(request)
    user = request.user if request.user.is_authenticated else None

    existing_reaction = Reaction.objects.filter(
        blog=blog_post,
        type=reaction_type,
        user=user if user else None,
        session_key=None if user else session_key
    ).first()

    if existing_reaction:
        existing_reaction.delete()
        action = 'removed'
    else:
        # remove other reactions by same user/session
        Reaction.objects.filter(
            blog=blog_post,
            user=user if user else None,
            session_key=None if user else session_key
        ).delete()

        Reaction.objects.create(
            blog=blog_post,
            user=user,
            session_key=None if user else session_key,
            type=reaction_type
        )
        action = 'added'

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
        'reaction_html': render_to_string(
            'blog/blog_reaction_counts.html',
            {'post': blog_post, 'user': request.user}
        ),
        'reaction_counts': reaction_counts
    })

@require_POST
def add_comment(request, post_id):
    blog_post = get_object_or_404(Blog, id=post_id)
    content = request.POST.get('content', '').strip()

    if not content:
        return JsonResponse({'status': 'error', 'message': 'Comment cannot be empty'}, status=400)

    session_key = get_session_key(request)
    user = request.user if request.user.is_authenticated else None

    Comment.objects.create(
        blog=blog_post,
        user=user,
        session_key=None if user else session_key,
        content=content
    )

    return JsonResponse({
        'status': 'success',
        'comments_html': render_to_string(
            'blog/comments.html',
            {'post': blog_post, 'user': request.user}
        )
    })

@require_POST
@login_required
def add_reply(request, comment_id):
    parent_comment = get_object_or_404(Comment, id=comment_id)
    content = request.POST.get('content', '').strip()

    if not content:
        return JsonResponse({'status': 'error', 'message': 'Reply cannot be empty'}, status=400)

    session_key = get_session_key(request)
    user = request.user if request.user.is_authenticated else None

    Comment.objects.create(
        blog=parent_comment.blog,
        parent=parent_comment,
        user=user,
        session_key=None if user else session_key,
        content=content
    )

    return JsonResponse({
        'status': 'success',
        'replies_html': render_to_string(
            'blog/replies.html',
            {'replies': parent_comment.replies.all()}
        )
    })


def video_list(request):
    qs = (VideoPost.objects
          .filter(is_published=True)
          .order_by('-published_at', '-created_at')
          .select_related('category'))

    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    if q:
        qs = qs.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(category__name__icontains=q)
        )

    if category:
        # accept either slug or exact name
        qs = qs.filter(Q(category__slug=category) | Q(category__name__iexact=category))

    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, "blog/video_list.html", {
        "videos": page_obj.object_list,
        "page_obj": page_obj,
        "video_categories": VideoCategory.objects.all().order_by("name"),
        "blog_categories": dict(Blog.CATEGORY_CHOICES), 
        "current_category": category,
        "search_query": q,
    })


def video_detail(request, slug):
    video = get_object_or_404(VideoPost, slug=slug, is_published=True)
    # increment views atomically
    VideoPost.objects.filter(pk=video.pk).update(views=F("views") + 1)
    video.refresh_from_db(fields=["views"])
    return render(request, "blog/video_detail.html", {"video": video})

