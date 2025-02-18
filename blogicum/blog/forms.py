from django import forms

from .models import Post, User


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "text", "pub_date", "location", "category", "image")
