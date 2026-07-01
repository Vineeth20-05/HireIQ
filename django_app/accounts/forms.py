from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class RegisterForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "role",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update({
            "class": "input input-bordered w-full"
        })

        self.fields["email"].widget.attrs.update({
            "class": "input input-bordered w-full"
        })

        self.fields["role"].widget.attrs.update({
            "class": "select select-bordered w-full"
        })

        self.fields["password1"].widget.attrs.update({
            "class": "input input-bordered w-full"
        })

        self.fields["password2"].widget.attrs.update({
            "class": "input input-bordered w-full"
        })