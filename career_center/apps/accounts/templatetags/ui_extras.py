from django import template
from pathlib import Path

register = template.Library()


@register.filter
def dict_get(mapping, key):
    if isinstance(mapping, dict):
        return mapping.get(key, key)
    return key


@register.filter
def initials(full_name):
    if not full_name:
        return '—'
    parts = [p for p in str(full_name).split() if p]
    return ''.join(part[0].upper() for part in parts[:2])


@register.filter
def basename(path):
    if not path:
        return ''
    return Path(str(path)).name


@register.filter
def is_image_file(filename):
    if not filename:
        return False
    return str(filename).lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))
