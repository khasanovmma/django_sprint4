from django import forms

from .models import Post, User, Comment


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
