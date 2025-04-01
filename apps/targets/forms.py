from django import forms
from .models import Target


class TargetForm(forms.ModelForm):
    """Form for creating and updating Target objects."""

    class Meta:
        model = Target
        fields = [
            'name',
            'street_address',
            'city',
            'state',
            'zip_code',
            'phone_number',
            'email_address',
            'website',
            'owners',
            'property_manager',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'street_address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email_address': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'owners': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3}
            ),
            'property_manager': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
        }
