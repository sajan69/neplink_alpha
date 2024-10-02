from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'contact', 'password1', 'password2']

class PasswordResetForm(forms.Form):
    email = forms.EmailField()

    class Meta:
        fields = ['email']

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6, label="Enter OTP")

    class Meta:
        fields = ['otp']

class UserPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']

class PasswordResetConfirmForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
   
    class Meta:
        model = User
        fields = ['password1', 'password2']
