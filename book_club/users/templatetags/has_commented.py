from django import template
from books.models import Comment

register = template.Library()

@register .simple_tag
def has_commented(request, book):
    return Comment.objects.filter(book=book, author=request.user).exists()
