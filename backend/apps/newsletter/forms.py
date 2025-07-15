from django import forms
from .models import Subscriber

class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter your email',
                'class': 'w-full px-4 py-2 rounded-lg border dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-aniomaBlue'
            }),
        }
