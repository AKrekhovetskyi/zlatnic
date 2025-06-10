from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path

from users.views import UserPasswordChangeView, UserUpdateView, register_request

urlpatterns = [
    path("register/", register_request, name="register"),
    path("account/<int:pk>/", UserUpdateView.as_view(), name="account"),
    path(
        "account/password/",
        UserPasswordChangeView.as_view(template_name="registration/password_change_form.html"),
        name="password_change",
    ),
    path(
        "password/done/",
        auth_views.PasswordChangeDoneView.as_view(template_name="registration/password_change_done.html"),
        name="password_change_done",
    ),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]

app_name = "users"
