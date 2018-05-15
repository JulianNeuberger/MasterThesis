from django import forms
from django.contrib.auth.models import User

from user.models import UserProfile


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ['user']
