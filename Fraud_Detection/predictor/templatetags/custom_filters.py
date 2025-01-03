from django import template

register = template.Library()

@register.filter
def sub(value, arg):
    """Subtract arg from value"""
    try:
        return value - arg
    except (ValueError, TypeError):
        return value

@register.filter
def multiply(value, arg):
    """Multiply value by arg"""
    try:
        return value * arg
    except (ValueError, TypeError):
        return value

@register.filter
def percentage(value, arg):
    """Calculate percentage"""
    try:
        return (value / arg) * 100
    except (ValueError, TypeError, ZeroDivisionError):
        return 0