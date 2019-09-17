from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SingUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(max_length=254, help_text='eq. youremail@anyemail.com')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password', 'password2')
