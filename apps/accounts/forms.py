from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordResetForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class LoginForm(AuthenticationForm):
    """Custom login form."""
    
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
        label=_("Email")
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        label=_("Password")
    )
    
    error_messages = {
        'invalid_login': _(
            "Please enter a correct email and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
    }


class RegisterForm(UserCreationForm):
    """Form for user registration."""
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Apply form-control class and placeholders to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'email':
                field.widget.attrs['placeholder'] = 'Email Address'
            elif field_name in ['first_name', 'last_name']:
                field.widget.attrs['placeholder'] = field_name.replace('_', ' ').title()
            elif field_name in ['password1', 'password2']:
                field.widget.attrs['placeholder'] = 'Password'