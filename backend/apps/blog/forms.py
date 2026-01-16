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
        fields = [
            "title", 
            "description", 
            "category", 
            "video_file",
            "external_url", 
            "thumbnail", 
            "is_published", 
            "is_featured", 
            "published_at"
            ]
        
        widgets = {
            "published_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean(self):
        cleaned = super().clean()

        video_url = cleaned.get("video_file")
        external = cleaned.get("external_url")


        if not video_url and not external:
            raise forms.ValidationError(
                "Provide a video URL (S3 or external embed)."
            )
        if video_url and external:
            raise forms.ValidationError(
                "Choose either a video URL or an external embed URL, not both."
            )

        return cleaned

