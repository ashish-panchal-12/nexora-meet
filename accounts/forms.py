from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile


class RegisterForm(UserCreationForm):
    email      = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=True)
    last_name  = forms.CharField(max_length=50, required=True)
    
    mobile_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control custom-input',
                'placeholder': 'Mobile Number (Optional)'
            }
        )
    )

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control custom-input'})


class LoginForm(AuthenticationForm):

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control custom-input',
                'placeholder': 'Email address or mobile number'
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control custom-input',
                'placeholder': 'Password'
            }
        )
    )


class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50)
    last_name  = forms.CharField(max_length=50)
    email      = forms.EmailField()

    class Meta:
        model  = Profile
        fields = ['avatar', 'bio']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial  = self.user.last_name
            self.fields['email'].initial      = self.user.email
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control custom-input'})