

from django.db.models import Q
from django.utils import timezone

from blog.models import User


def get_user_allowed_posts_query(user: User):
    
    return Q(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    ) | Q(author=user)
