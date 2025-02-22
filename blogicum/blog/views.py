from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.http import (
    HttpRequest,
    HttpResponse,
    Http404,
)

from blog.forms import CommentForm, EditProfileForm, PostForm
from blog.models import Category, Comment, Post, User
from blog.selectors import get_post_queryset, paginate_queryset


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
    page_obj = paginate_queryset(
        queryset=get_post_queryset(use_filters=True, add_annotations=True),
        request=request,
    )
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
    post = get_object_or_404(
        get_post_queryset(),
        pk=post_id,
    )

    if post.author != request.user and (
        not post.is_published
        or not post.category.is_published
        or post.pub_date > timezone.now()
    ):
        raise Http404("Публикация недоступна.")

    form = CommentForm()
    template = "blog/detail.html"
    return render(
        request=request,
        template_name=template,
        context={
            "post": post,
            "form": form,
            "comments": post.comments.all().select_related("author"),
        },
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
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    page_obj = paginate_queryset(
        queryset=get_post_queryset(
            use_filters=True,
            add_annotations=True,
        ).filter(category=category),
        request=request,
    )
    return render(
        request=request,
        template_name=template,
        context={"category": category, "page_obj": page_obj},
    )


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
    if request.user == user:
        post_queryset = get_post_queryset(add_annotations=True)
    else:
        post_queryset = get_post_queryset(
            use_filters=True,
            add_annotations=True,
        )
    page_obj = paginate_queryset(
        queryset=post_queryset.filter(author=user), request=request
    )
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
    form = EditProfileForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect("blog:profile", username=request.user.username)
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
        return redirect("blog:profile", username=request.user.username)
    return render(request, "blog/create.html", context={"form": form})


@login_required
def edit_post(request: HttpRequest, post_id: int) -> HttpResponse:
    """
    Обрабатывает редактирование существующего поста.

    Требует аутентификации. Получает пост по его ID. Если текущий пользователь
    не является автором поста, возвращает ошибку 403. При валидной форме
    сохраняет изменения и перенаправляет пользователя на страницу профиля.

    Args:
        request (HttpRequest): Запрос от пользователя.
        post_id (int): Идентификатор редактируемого поста.

    Returns:
        HttpResponse: Страница редактирования поста или редирект на профиль.
    """
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author:
        return redirect("blog:post_detail", post_id=post_id)

    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect("blog:profile", username=request.user.username)
    return render(request, "blog/create.html", context={"form": form})


@login_required
def delete_post(request: HttpRequest, post_id: int) -> HttpResponse:
    """
    Удаляет пост, если текущий пользователь является его автором.

    Для выполнения операции требуется аутентификация. Если пользователь не
    является автором поста, выполняется редирект на страницу его профиля.
    При успешном удалении также происходит редирект на страницу профиля.

    Аргументы:
        request (HttpRequest): Входящий HTTP-запрос.
        post_id (int): Идентификатор удаляемого поста.

    Возвращает:
        HttpResponse: Редирект на страницу профиля пользователя.
    """
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect("blog:profile", username=request.user.username)
    post.delete()
    return redirect("blog:profile", username=request.user.username)


@login_required
def add_comment(request: HttpRequest, post_id: int) -> HttpResponse:
    """
    Обрабатывает добавление комментария к посту.

    Только авторизованные пользователи могут оставлять комментарии.
    Функция получает объект поста по переданному `post_id` и проверяет данные
    формы.Если форма валидна, создаётся комментарий, привязанный к посту и
    пользователю.После сохранения комментария происходит редирект на страницу
    поста.

    Args:
        request (HttpRequest): Запрос от пользователя.
        post_id (int): Идентификатор поста, к которому добавляется комментарий.

    Returns:
        HttpResponse: Редирект на страницу деталей поста.
    """
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment: Comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("blog:post_detail", post_id)


@login_required
def edit_comment(
    request: HttpRequest,
    post_id: int,
    comment_id: int,
) -> HttpResponse:
    """
    Редактирование комментария к посту.

    Функция получает идентификаторы поста и комментария, проверяет,
    является ли текущий пользователь автором комментария. Если нет —
    перенаправляет на страницу поста. Если да — отображает форму для
    редактирования комментария. При успешной валидации сохраняет изменения
    и перенаправляет пользователя обратно к посту.

    Аргументы:
        request (HttpRequest): Объект запроса.
        post_id (int): Идентификатор поста.
        comment_id (int): Идентификатор комментария.

    Возвращает:
        HttpResponse: Страница с формой редактирования комментария или
                      перенаправление на страницу поста.
    """
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    if request.user != comment.author:
        return redirect("blog:post_detail", post_id)

    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect("blog:post_detail", post_id)
    return render(request, "blog/create.html", context={"form": form})


@login_required
def delete_comment(
    request: HttpRequest,
    post_id: int,
    comment_id: int,
) -> HttpResponse:
    """
    Удаляет комментарий, если текущий пользователь является его автором.

    Если пользователь не является автором комментария, выполняется редирект на
    страницу поста. В случае успешного удаления также происходит редирект на
    страницу поста.При GET-запросе отображается страница с подтверждением
    удаления комментария.

    Аргументы:
        request (HttpRequest): HTTP-запрос пользователя.
        post_id (int): Идентификатор поста, к которому относится комментарий.
        comment_id (int): Идентификатор удаляемого комментария.

    Возвращает:
        HttpResponse: Редирект на страницу поста после удаления или
        отображение страницы подтверждения удаления при GET-запросе.
    """
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    if request.user != comment.author:
        return redirect("blog:post_detail", post_id)

    if request.method == "POST":
        comment.delete()
        return redirect(
            reverse_lazy(
                "blog:post_detail",
                kwargs={
                    "post_id": post_id,
                },
            )
        )

    return render(request, "blog/comment.html", context={"comment": comment})
