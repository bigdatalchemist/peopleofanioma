from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'placeholder': 'Enter username',
            'class': 'w-full p-2 border border-gray-300 rounded'
        })
        self.fields['username'].help_text = "150 characters or fewer. Letters, digits and @/./+/-/_ only."
        
        self.fields['email'].widget.attrs.update({
            'placeholder': 'Enter email',
            'class': 'input-field'
        })

        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Enter password',
            'class': 'w-full p-2 border border-gray-300 rounded'
        })
        self.fields['password1'].help_text = (
            "Your password must contain at least 8 characters, cannot be too similar to personal info, "
            "must not be a common password, and cannot be entirely numeric."
        )

        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm password',
            'class': 'w-full p-2 border border-gray-300 rounded'
        })
        self.fields['password2'].help_text = "Enter the same password as above for verification."

class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'placeholder': 'Enter your username',
            'class': 'w-full p-2 border border-gray-300 rounded'
        })

        self.fields['password'].widget.attrs.update({
            'placeholder': 'Enter your password',
            'class': 'w-full p-2 border border-gray-300 rounded'
        })
    remember_me = forms.BooleanField(required=False, initial=False, label='Remember Me')

class BioUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['bio']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border rounded-lg',
                'rows': 3,
                'placeholder': 'Tell us about yourself...'
            })
        }

class ProfilePictureUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-orange-50 file:text-orange-700 hover:file:bg-orange-100'
            })
        }