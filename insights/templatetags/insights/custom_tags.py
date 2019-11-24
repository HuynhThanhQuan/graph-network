from django import template

register = template.Library()


@register.filter
def index(lst, index):
    lst = list(lst)
    item = lst[int(index)]
    return item
