from django import template
register = template.Library()

@register.filter(name="get_value")
def get_value(dictionary, i):
    return dictionary[i-1]

@register.filter(name="get_first")
def get_first(dictionary):
    return list(dictionary.values())[0]