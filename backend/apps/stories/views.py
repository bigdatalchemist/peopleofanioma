# stories/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Story, Comment
from .forms import StoryForm
from django.core.paginator import Paginator
from django.db.models import Q
from .utils.moderation import auto_moderate_story
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

@login_required

def story_list(request):
    query = request.GET.get('q')
    all_stories = Story.objects.filter(is_approved=True).order_by('-date_submitted')
    if query:
        all_stories = all_stories.filter(Q(title__icontains=query) | Q(category__icontains=query))

    # Separate current user's stories to "pin" them at the top
    user_stories = []
    if request.user.is_authenticated:
        user_stories = all_stories.filter(user=request.user)
        all_stories = all_stories.exclude(user=request.user)

    combined_stories = list(user_stories) + list(all_stories)

    paginator = Paginator(combined_stories, 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    return render(request, 'stories/story_list.html', {
        'page_obj': page_obj,
        'query': query,
        'user_stories': user_stories if request.user.is_authenticated else []
    })
    
@login_required
def user_profile(request):
    user_stories = Story.objects.filter(user=request.user).order_by('-date_submitted')
    return render(request, 'stories/user_profile.html', {'user_stories': user_stories})

def story_detail(request, slug):
    story = get_object_or_404(Story, slug=slug, is_approved=True)
    return render(request, 'stories/story_detail.html', {'story': story})

@login_required
def submit_story(request):
    if request.method == 'POST':
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.user = request.user
            story.author_name = request.user.username

            # Step 2: Run AI moderation
            if auto_moderate_story(story.title, story.content):
                story.is_approved = True  # Auto-approve
            else:
                story.is_approved = False  # Requires admin review

            story.save()
            return redirect('story_thank_you')
    else:
        form = StoryForm()
    return render(request, 'stories/submit_story.html', {'form': form})

def like_story(request, slug):
    story = get_object_or_404(Story, slug=slug)
    user = request.user
    if user in story.likes.all():
        story.likes.remove(user)
        liked = False
    else:
        story.likes.add(user)
        liked = True
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked, 'likes_count': story.likes.count()})
    return redirect('story_detail', slug=slug)

def upvote_story(request, slug):
    story = get_object_or_404(Story, slug=slug)
    story.upvotes += 1
    story.save()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'upvotes': story.upvotes})
    return redirect('story_detail', slug=slug)


def add_comment(request, slug):
    if request.method == 'POST':
        story = get_object_or_404(Story, slug=slug)
        content = request.POST.get('content')
        if content:
            Comment.objects.create(story=story, user=request.user, content=content)
        return redirect('story_detail', slug=slug)


def thank_you(request):
    return render(request, 'stories/thank_you.html')