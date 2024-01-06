from django import template

register = template.Library()

@register.filter
def concat(value, arg):
    return '_'.join(str(x) for x in sorted([str(value), str(arg)]))

