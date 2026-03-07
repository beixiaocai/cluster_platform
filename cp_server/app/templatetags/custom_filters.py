from django import template
from datetime import datetime

register = template.Library()

@register.filter(name='timestamp')
def timestamp(value, format_string='%Y/%m/%d %H:%M'):
    if not value:
        return '-'
    try:
        dt = datetime.fromtimestamp(int(value))
        return dt.strftime(format_string)
    except (ValueError, TypeError):
        return '-'
