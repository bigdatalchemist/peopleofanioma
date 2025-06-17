# apps/diaspora_tracker/forms.py
from django import forms
from .models import DiasporaEntry

class DiasporaEntryForm(forms.ModelForm):
    class Meta:
        model = DiasporaEntry
        fields = [
            'name', 'email', 'country', 'city', 'profession',
            'year_migrated', 'local_origin', 'reason_for_migrating'
        ]
        widgets = {
            'reason_for_migrating': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-orange-500 focus:border-orange-500 dark:bg-gray-700 dark:text-white'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Base styling for all inputs
        base_attrs = {
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-orange-500 focus:border-orange-500 dark:bg-gray-700 dark:text-white',
        }
        
        # Apply to all fields except those with custom widgets
        for field_name, field in self.fields.items():
            if field_name not in ['reason_for_migrating']:  # Skip already customized fields
                field.widget.attrs.update(base_attrs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and not email.endswith(('.com', '.org', '.edu', '.gov', '.net')):
            raise forms.ValidationError("Please enter a valid institutional or professional email.")
        return email