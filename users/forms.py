import re
from typing import Any

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            placeholder = field_name.replace("_", " ").title()
            placeholder = "Password Confirmation" if placeholder == "Password2" else re.sub(r"\d+", "", placeholder)
            field.widget.attrs.update({"class": "input_data", "placeholder": placeholder})

    class Meta:
        model = get_user_model()
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
            "phone_number",
        )

    def save(self, *, commit: bool = True) -> Any:  # type: ignore[BaseUserCreationForm]
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.save(commit)
        return user


class UserAccountForm(UserChangeForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            placeholder = field_name.replace("_", " ").title()
            field.widget.attrs.update({"class": "input_data", "placeholder": placeholder})

    class Meta:
        model = get_user_model()
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "phone_number",
            "image",
        )
