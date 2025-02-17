from django.shortcuts import get_object_or_404, render

from blog.constants import POSTS_LIMIT
from .models import Category
from .selectors import get_active_post_queryset


def index(request):
    """
    Главная страница блога.

    Отображает список последних опубликованных публикаций
    (максимум POSTS_LIMIT),которые опубликованы, имеют дату
    публикации в прошлом или настоящем, и относятся к опубликованным
    категориям.

    Аргументы:
        request: HttpRequest.

    Возвращает:
        HttpResponse.
    """
    template = "blog/index.html"
    return render(
        request=request,
        template_name=template,
        context={"post_list": get_active_post_queryset()[:POSTS_LIMIT]},
    )


def post_detail(request, post_id):
    """
    Детальная страница публикации.

    Отображает информацию о конкретной публикации, которая опубликована,
    имеет дату публикации в прошлом или настоящем,
    и относится к опубликованной категории.

    Аргументы:
        request: HttpRequest.
        post_id: Идентификатор публикации.

    Возвращает:
        HTTP-ответ с деталями публикации.
    """
    post = get_object_or_404(get_active_post_queryset(), pk=post_id)
    template = "blog/detail.html"
    return render(
        request=request,
        template_name=template,
        context={"post": post},
    )


def category(request, category_slug):
    """
    Страница категории блога.

    Отображает список публикаций, относящихся к конкретной категории,
    которая опубликована, а также имеет дату публикации в прошлом или
    настоящем.

    Аргументы:
        request: HttpRequest.
        category_slug: Уникальный идентификатор категории (slug).

    Возвращает:
        HttpResponse.
    """
    template = "blog/category.html"
    category_obj = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    post_list = get_active_post_queryset().filter(category=category_obj)

    return render(
        request=request,
        template_name=template,
        context={"category": category_obj, "post_list": post_list},
    )
