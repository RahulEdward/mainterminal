from django import forms
from .models import User

class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'client_id', 'api_key']

class LoginForm(forms.Form):
    client_id = forms.CharField(max_length=100)
    pin = forms.CharField(widget=forms.PasswordInput())
    totp = forms.CharField(widget=forms.PasswordInput())
