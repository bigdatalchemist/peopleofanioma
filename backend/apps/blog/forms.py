# blog/forms.py
from django import forms
from .models import Blog

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