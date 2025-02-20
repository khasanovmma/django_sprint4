from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Post, User, Comment


class CreateProfileForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        )


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "text", "pub_date", "location", "category", "image")


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
