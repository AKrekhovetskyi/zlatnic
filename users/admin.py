from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin


@admin.register(get_user_model())
class UserAdmin(DefaultUserAdmin):
    fieldsets = (("Additional info", {"fields": ("phone_number", "image")}), *DefaultUserAdmin.fieldsets)
    add_fieldsets = (
        (
            (
                "Additional info",
                {"fields": ("first_name", "last_name", "phone_number", "image")},
            )
        ),
        *DefaultUserAdmin.add_fieldsets,
    )
    list_display = ("phone_number", "image", *DefaultUserAdmin.list_display)
