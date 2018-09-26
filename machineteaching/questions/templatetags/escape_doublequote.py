from django import template

register = template.Library()

@register.filter
def escape_doublequote(value):
    return value.replace('"', '\"')
