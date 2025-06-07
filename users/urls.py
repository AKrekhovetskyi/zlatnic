from django.urls import path

from users.views import UserUpdateView, register_request

urlpatterns = [
    path("register/", register_request, name="register"),
    path("account/<int:pk>/", UserUpdateView.as_view(), name="account"),
]

app_name = "users"
