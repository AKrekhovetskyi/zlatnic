from typing import Any

from django import template
from django.core.handlers.wsgi import WSGIRequest

register = template.Library()


@register.simple_tag
def query_transform(request: WSGIRequest, **kwargs: Any) -> str:
    updated = request.GET.copy()
    for key, value in kwargs.items():
        if value is not None:
            updated[key] = value
        else:
            updated.pop(key, 0)

    return updated.urlencode()
