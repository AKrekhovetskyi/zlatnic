from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import generic

from users.forms import NewUserForm, UserAccountForm


def register_request(request: WSGIRequest) -> HttpResponseRedirect | HttpResponse:
    """User registration function-based view."""
    form = NewUserForm
    if request.method == "POST":
        form = form(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("manager:wallets")
        return render(request, "registration/register.html", {"form": form})
    return render(request, "registration/register.html", {"form": form()})


class UserUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = get_user_model()
    form_class = UserAccountForm
    success_url = reverse_lazy("manager:index")
