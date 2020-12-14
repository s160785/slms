from django import template
register = template.Library()


@register.filter
def index(indexable, i):
    return indexable[i]


@register.filter
def sub(value, args):
    print(value, args)
    return args-value
