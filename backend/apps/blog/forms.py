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
        fields = ["title", "description", "category", "external_url", "thumbnail", "is_published", "is_featured", "published_at"]
        widgets = {
            "published_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean(self):
        cleaned = super().clean()

        url = cleaned.get("external_url")

        if not url:
            raise forms.ValidationError(
                "Provide a video URL (S3 or external embed)."
            )

        return cleaned

