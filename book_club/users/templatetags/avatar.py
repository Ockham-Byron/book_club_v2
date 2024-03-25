from django import template
from django.template.loader import render_to_string


register = template.Library()


@register.filter
def avatar(user):
    letter = user.username[0].upper() if user.username else '?'
    color = user.avatar_color
    context = {'color': color, 'letter': letter}
    return render_to_string('users/avatar.svg', context)
