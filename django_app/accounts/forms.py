from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class RegisterForm(UserCreationForm):

    class Meta:
        model=CustomUser

        fields=[
            'username',
            'email',
            'role',
            'password1',
            'password2'
        ]

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values():
            field.widget.attrs.update(
                {
                    'class':'input input-bordered w-full'
                }
            )