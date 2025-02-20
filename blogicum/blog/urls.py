from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.index, name="index"),
    path("posts/<int:post_id>/", views.post_detail, name="post_detail"),
    path("posts/create/", views.create_post, name="create_post"),
    path("posts/<int:post_id>/edit/", views.edit_post, name="edit_post"),
    path("posts/<int:post_id>/delete/", views.delete_post, name="delete_post"),
    path(
        "posts/<int:post_id>/comment/",
        views.add_comment,
        name="add_comment",
    ),
    path(
        "posts/<int:post_id>/edit_comment/<int:comment_id>/edit/",
        views.edit_comment,
        name="edit_comment",
    ),
    path(
        "category/<slug:category_slug>/",
        views.category,
        name="category_posts",
    ),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path("profile/<str:username>/", views.detail_profile, name="profile"),
]
