from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from users.views import UserUpdateView, register_request

urlpatterns = [
    path("register/", register_request, name="register"),
    path("account/<int:pk>/", UserUpdateView.as_view(), name="account"),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]

app_name = "users"
