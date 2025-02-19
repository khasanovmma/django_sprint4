from django.contrib import admin

from .models import Category, Location, Post, Comment

admin.site.empty_value_display = "Не задано"


class CommentInline(admin.StackedInline):
    model = Comment
    raw_id_fields = ("author",)
    extra = 0


class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "category",
        "pub_date",
        "is_published",
        "created_at",
    )
    inlines = (CommentInline,)
    raw_id_fields = ("author", "location", "category")


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published", "created_at")


class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "is_published", "created_at")


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
