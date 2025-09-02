# blog/forms.py
from django import forms
from .models import Blog, VideoPost

class BlogSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label='Search',
        widget=forms.TextInput(attrs={
            'placeholder': 'Search posts...',
            'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500'
        })
    )
    category = forms.ChoiceField(
        required=False,
        label='Category',
        choices=Blog.CATEGORY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500'
        })
    )

class VideoPostForm(forms.ModelForm):
    class Meta:
        model = VideoPost
        fields = ["title", "description", "category", "video_file", "external_url", "thumbnail", "is_published", "is_featured", "published_at"]
        widgets = {
            "published_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean(self):
        cleaned = super().clean()
        file = cleaned.get("video_file")
        url = cleaned.get("external_url")
        if not file and not url:
            raise forms.ValidationError("Provide a video file or an external video URL.")
        if file and url:
            raise forms.ValidationError("Choose either a video file or an external URL, not both.")
        if file:
            # Optional: basic validation (MIME/size)
            max_mb = 200  # tweak for your infra
            if file.size > max_mb * 1024 * 1024:
                raise forms.ValidationError(f"Video too large (>{max_mb}MB).")
        return cleaned
