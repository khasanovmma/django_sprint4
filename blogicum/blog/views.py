from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse

from blog.constants import POSTS_LIMIT
from .forms import EditProfileForm, PostForm
from .models import Category, Post, User
from .selectors import get_active_post_queryset


def index(request: HttpRequest) -> HttpResponse:
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


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
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


def category(request: HttpRequest, category_slug: str) -> HttpResponse:
    """
    Страница категории блога.

    Отображает список публикаций (максимум POSTS_LIMIT), относящихся к
    конкретной категории, которая опубликована, а также имеет дату
    публикации в прошлом илинастоящем.

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
    paginator = Paginator(post_list, POSTS_LIMIT)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request=request,
        template_name=template,
        context={"category": category_obj, "page_obj": page_obj},
    )


@login_required
def detail_profile(request: HttpRequest, username: str) -> HttpResponse:
    """
    Отображает страницу профиля пользователя с его постами.

    Требует аутентификации.

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


@login_required
def edit_profile(request: HttpRequest) -> HttpResponse:
    """
    Обрабатывает редактирование профиля пользователя.

    Требует аутентификации. Загружает данные текущего пользователя,
    передает их в форму редактирования и сохраняет изменения,если форма
    валидна.После успешного сохранения происходит xредирект на страницу
    профиля.

    Args:
        request (HttpRequest): Запрос от пользователя.

    Returns:
        HttpResponse: Страница редактирования профиля с формой или
        редирект на профиль пользователя после успешного обновления.
    """
    user = get_object_or_404(User, username=request.user.username)
    form = EditProfileForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        return redirect(
            "blog:profile",
            username=user.username,
        )
    return render(request, "blog/user.html", context={"form": form})


@login_required
def create_post(request: HttpRequest) -> HttpResponse:
    """
    Обрабатывает создание нового поста.

    Требует аутентификации. Создаёт форму для ввода данных поста.
    Если форма валидна, создаёт объект, назначает автора и сохраняет.
    После успешного сохранения выполняется редирект на профиль.

    Args:
        request (HttpRequest): Запрос от пользователя.

    Returns:
        HttpResponse: Страница с формой или редирект на профиль.
    """
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        post: Post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(
            "blog:profile",
            username=request.user.username,
        )
    return render(request, "blog/create.html", context={"form": form})
