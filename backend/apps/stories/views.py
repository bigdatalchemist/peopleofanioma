# stories/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Story, Comment, StoryReaction
from .forms import StoryForm
from django.core.paginator import Paginator
from django.db.models import Q
from .utils.moderation import auto_moderate_story
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.template.loader import render_to_string


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
            return redirect('stories:story_thank_you')
    else:
        form = StoryForm()
    return render(request, 'stories/submit_story.html', {'form': form})

@require_POST 
def add_story_reaction(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    reaction_type = request.POST.get('reaction')
    
    if not reaction_type:
        return JsonResponse({'status': 'error', 'message': 'Reaction type required'}, status=400)
    
    # Check if user already has this reaction
    existing_reaction = StoryReaction.objects.filter(
        user=request.user,
        story=story,
        type=reaction_type
    ).first()
    
    if existing_reaction:
        existing_reaction.delete()  # Toggle reaction off
        action = 'removed'
    else:
        # Remove any existing reaction of different type
        StoryReaction.objects.filter(user=request.user, story=story).delete()
        # Add new reaction
        StoryReaction.objects.create(
            user=request.user,
            story=story,
            type=reaction_type
        )
        action = 'added'
    
    # Return updated reaction counts
    reaction_counts = {
        'like': story.reactions.filter(type='like').count(),
        'love': story.reactions.filter(type='love').count(),
        'clap': story.reactions.filter(type='clap').count(),
        'insightful': story.reactions.filter(type='insightful').count(),
        'laugh': story.reactions.filter(type='laugh').count(),
    }
    
    return JsonResponse({
        'status': 'success',
        'action': action,
        'reaction': reaction_type,
        'reaction_html': render_to_string('stories/reaction_counts.html', {
            'story': story,
            'user': request.user
        }),
        'reaction_counts': reaction_counts
    })


def add_comment(request, slug):
    if request.method == 'POST':
        story = get_object_or_404(Story, slug=slug)
        content = request.POST.get('content')
        if content:
            Comment.objects.create(story=story, user=request.user, content=content)
        return redirect('stories:story_detail', slug=slug)


def thank_you(request):
    return render(request, 'stories/thank_you.html')

@login_required
def edit_story(request, slug):
    story = get_object_or_404(Story, slug=slug, user=request.user)
    if request.method == 'POST':
        form = StoryForm(request.POST, request.FILES, instance=story)
        if form.is_valid():
            form.save()
            messages.success(request, "Story updated successfully.")
            return redirect('stories:story_detail', slug=story.slug)
    else:
        form = StoryForm(instance=story)
    return render(request, 'stories/edit_story.html', {'form': form, 'story': story})


@login_required
def delete_story(request, slug):
    story = get_object_or_404(Story, slug=slug)

    if story.user != request.user:
        return HttpResponseForbidden("You are not allowed to delete this story.")

    if request.method == 'POST':
        story.delete()
        messages.success(request, "Story deleted successfully.")
        return redirect('users:profile')

    return render(request, 'stories/confirm_delete.html', {'story': story})
