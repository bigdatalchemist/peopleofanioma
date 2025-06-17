from django import forms
from .models import EthnographicSurvey

class EthnographicSurveyForm(forms.ModelForm):
    class Meta:
        model = EthnographicSurvey
        fields = [
            'name',
            'age',
            'gender',
            'occupation',
            'village',
            'local_origin',
            'location',
            'cultural_practice',
            'oral_history',
            'language_spoken',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Enter your full name',
                'class': 'w-full p-2 border rounded placeholder-gray-500'
            }),
            'age': forms.NumberInput(attrs={
                'placeholder': 'Enter your age',
                'class': 'w-full p-2 border rounded placeholder-gray-500'
            }),
            'gender': forms.TextInput(attrs={
                'placeholder': 'Enter your gender',
                'class': 'w-full p-2 border rounded placeholder-gray-500'
            }),
            'occupation': forms.TextInput(attrs={
                'placeholder': 'Enter your occupation',
                'class': 'w-full p-2 border rounded placeholder-gray-500'
            }),
            'village': forms.TextInput(attrs={
                'placeholder': 'Enter your village',
                'class': 'w-full p-2 border rounded placeholder-gray-500'
            }),
            'local_origin': forms.Select(attrs={
                'placeholder': 'Enter your local government area',
                'class': 'w-full p-2 border rounded placeholder-gray-500'
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'Enter your current location',
                'class': 'w-full p-2 border rounded placeholder-gray-500'
            }),
            'cultural_practice': forms.Textarea(attrs={
                'placeholder': 'Describe any known cultural practices',
                'class': 'w-full p-2 border rounded placeholder-gray-500',
                'rows': 3
            }),
            'oral_history': forms.Textarea(attrs={
                'placeholder': 'Share any relevant oral history',
                'class': 'w-full p-2 border rounded placeholder-gray-500',
                'rows': 3
            }),
            'language_spoken': forms.TextInput(attrs={
                'placeholder': 'Enter language(s) spoken',
                'class': 'w-full p-2 border rounded placeholder-gray-500'
            }),
        }
