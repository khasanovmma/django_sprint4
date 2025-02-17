from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator

from blog.constants import POSTS_LIMIT
from .models import Category, User
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
    paginator = Paginator(get_active_post_queryset(), POSTS_LIMIT)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request=request, template_name=template, context={"page_obj": page_obj}
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


def detail_profile(request, username: str):
    """
    Отображает страницу профиля пользователя с его постами.

    Аргументы:
        request: HTTP-запрос.
        username: (str) Имя пользователя, чей профиль нужно отобразить.

    Возвращает:
        HttpResponse: Страница профиля пользователя с пагинацией постов.
    """
    user = get_object_or_404(User, username=username)
    posts = user.posts.all()
    paginator = Paginator(posts, POSTS_LIMIT)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"profile": user, "page_obj": page_obj}
    return render(request, "blog/profile.html", context=context)
