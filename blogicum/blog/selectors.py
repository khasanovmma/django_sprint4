from django.utils import timezone

from .models import Post


def get_active_post_queryset():
    """Возвращает базовый QuerySet для публикации."""
    return Post.objects.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True,
    ).select_related("author", "location", "category")
