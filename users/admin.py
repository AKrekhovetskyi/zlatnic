from typing import Any

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.http import HttpRequest

fields = ("phone_number", "image")
additional_info = ("Additional info", {"fields": fields})


@admin.register(get_user_model())
class UserAdmin(DefaultUserAdmin):
    list_display = (*DefaultUserAdmin.list_display, *fields)  # type: ignore[reportGeneralTypeIssues]

    def get_fieldsets(self, request: HttpRequest, obj: Any | None = None) -> Any:
        fieldsets = super().get_fieldsets(request, obj)
        return (*fieldsets, additional_info)
