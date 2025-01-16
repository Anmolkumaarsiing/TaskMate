# tasks/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.forms import PasswordChangeForm

class SignUpForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())


# tasks/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Profile

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']  # Include first_name and last_name

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['dob', 'bio', 'phone_number', 'qualifications']  # Ensure phone_number is included

    # Optional: You can add custom validation or formatting here for the phone number.
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        # Add any phone number validation logic if needed
        return phone_number
