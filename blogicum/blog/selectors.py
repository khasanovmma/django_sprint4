from django.db.models import Count, QuerySet
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import HttpRequest

from blog.models import Post
from blog.constants import POSTS_LIMIT


def get_post_queryset(
    use_filters=False,
    add_annotations=False,
) -> QuerySet[Post]:
    """
    Возвращает базовый QuerySet для публикаций с возможностью фильтрации
    и аннотации.

    :param use_filters: Учитывать фильтры (скрытые и отложенные посты).
    :param add_annotations: Добавлять аннотации и сортировку.
    :return: QuerySet[Post]
    """
    queryset = Post.objects.select_related("author", "location", "category")
    if use_filters:
        queryset = queryset.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        )
    if add_annotations:
        queryset = queryset.annotate(comment_count=Count("comments")).order_by(
            "-pub_date"
        )
    return queryset


def paginate_queryset(
    queryset: QuerySet, request: HttpRequest, posts_limit: int = POSTS_LIMIT
) -> QuerySet:
    """
    Функция для пагинации списка записей.

    :param queryset: QuerySet[Post] для пагинации.
    :param request: HTTP-запрос с параметрами.
    :param posts_limit: Лимит записей на страницу.
    :return: объект страницы.
    """
    paginator = Paginator(queryset, posts_limit)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
