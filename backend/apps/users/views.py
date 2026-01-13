# apps/users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm, CustomLoginForm, BioUpdateForm, ProfilePictureUpdateForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from apps.diaspora_tracker.forms import DiasporaEntryForm
from apps.diaspora_tracker.models import DiasporaEntry
from apps.stories.forms import StoryForm
from apps.stories.models import Story
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.contrib import messages


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('users:profile')  # change to your actual redirect target
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    authentication_form = CustomLoginForm
    
    def form_valid(self, form):
        remember = self.request.POST.get('remember_me')
        if not remember:
            # Set session to expire when the browser closes
            self.request.session.set_expiry(0)
        else:
            # Session will last for e.g. 2 weeks (default)
            self.request.session.set_expiry(1209600)
        return super().form_valid(form)

@login_required
def profile(request):
    if request.method == 'POST':
        if 'diaspora_submit' in request.POST:
            diaspora_form = DiasporaEntryForm(request.POST)
            if diaspora_form.is_valid():
                entry = diaspora_form.save(commit=False)
                entry.user = request.user
                entry.save()
                return redirect('users:profile')
    
    approved_stories = Story.objects.filter(
        user=request.user,
        is_approved=True
    ).order_by('-date_submitted')

    user_stories = Story.objects.filter(
        user=request.user
    ).order_by('-date_submitted')

    diaspora_entries = DiasporaEntry.objects.filter(
        email=request.user.email
    ).order_by('-timestamp')
    
    context = {
        'diaspora_form': DiasporaEntryForm(),
        'story_form': StoryForm(),
        'approved_stories': approved_stories,
        'diaspora_entries': diaspora_entries,
        'diaspora_tracker_url': reverse_lazy('diaspora_tracker'),
        'user_stories': Story.objects.filter(user=request.user).order_by('-date_submitted'), 
    }
    return render(request, 'users/profile.html', context)

@login_required
def update_profile_pic(request):
    if request.method == 'POST':
        form = ProfilePictureUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile picture updated successfully!')
            return redirect('users:profile')
    else:
        form = ProfilePictureUpdateForm(instance=request.user)
    
    return render(request, 'users/update_profile_pic.html', {'form': form})

@login_required
def delete_profile_pic(request):
    if request.method == 'POST':
        request.user.profile_pics.delete(save=True)  # This will remove the profile picture
        messages.success(request, 'Profile picture removed successfully!')
        return redirect('users:profile')
    
    return render(request, 'users/confirm_delete_pic.html')

@login_required
def edit_bio(request):
    if request.method == 'POST':
        form = BioUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bio updated successfully!')
            return redirect('users:profile')
    else:
        form = BioUpdateForm(instance=request.user)
    
    return render(request, 'users/edit_bio.html', {'form': form})