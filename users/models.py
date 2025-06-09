import uuid
from pathlib import Path

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField


def user_image_file_path(instance: "User", filename: str) -> Path:
    extension = Path(filename).suffix
    filename = f"{slugify(instance.username)}-{uuid.uuid4()}{extension}"

    return Path("profile_picture").joinpath(filename)


class User(AbstractUser):
    email = models.EmailField(null=False, blank=False)
    phone_number = PhoneNumberField(blank=True)
    image = models.ImageField(null=True, blank=True, upload_to=user_image_file_path)
