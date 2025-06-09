from typing import Any, cast

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Manager, Q, QuerySet, Sum
from django.db.models.functions import Round, TruncMonth
from django.http.response import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from manager.forms import AccountancyForm, AccountancySearchForm
from manager.models import Accountancy, Card, Cash, Cryptocurrency
from manager.wallet_operations import change_wallet_balance, monthly_financial_turnover, wallet_choice


def wallet_objects(request: WSGIRequest) -> tuple[QuerySet, QuerySet, QuerySet]:
    user = request.user
    cards = user.cards.select_related("currency")  # type: ignore[reportAttributeAccessIssue]
    cash_types = user.cash.select_related("currency")  # type: ignore[reportAttributeAccessIssue]
    crypto = user.cryptocurrencies.all()  # type: ignore[reportAttributeAccessIssue]

    return cards, cash_types, crypto


@login_required
def wallets(request: WSGIRequest) -> HttpResponse:
    cards, cash_types, crypto = wallet_objects(request)

    context = {
        "cards_list": cards,
        "cash_list": cash_types,
        "crypto_list": crypto,
    }
    return render(request, "manager/wallets.html", context)


class CardCreateView(LoginRequiredMixin, generic.CreateView):
    model = Card
    fields = (
        "user",
        "bank_name",
        "type",
        "balance",
        "currency",
    )
    success_url = reverse_lazy("manager:wallets")


class CardUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Card
    fields = (
        "user",
        "bank_name",
        "type",
        "currency",
    )
    success_url = reverse_lazy("manager:wallets")


class CardDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Card
    success_url = reverse_lazy("manager:wallets")


class CashCreateView(LoginRequiredMixin, generic.CreateView):
    model = Cash
    fields = (
        "user",
        "currency",
    )
    success_url = reverse_lazy("manager:wallets")


class CashUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Cash
    fields = (
        "user",
        "currency",
    )
    success_url = reverse_lazy("manager:wallets")


class CashDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Cash
    success_url = reverse_lazy("manager:wallets")


class CryptoCreateView(LoginRequiredMixin, generic.CreateView):
    model = Cryptocurrency
    fields = (
        "user",
        "name",
    )
    success_url = reverse_lazy("manager:wallets")


class CryptoUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Cryptocurrency
    fields = (
        "user",
        "name",
    )
    success_url = reverse_lazy("manager:wallets")


class CryptoDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Cryptocurrency
    success_url = reverse_lazy("manager:wallets")


@login_required
def index(request: WSGIRequest) -> HttpResponse:
    """Function-based view for the base page of the site."""
    wallets_set: list[list[str | Card | Cash | Cryptocurrency]] = []
    error = False
    income = outcome = 0
    accountancy = Accountancy.objects

    cards, cash_types, crypto = wallet_objects(request)

    if cards:
        wallets_set.extend([f"card - {card.id}", card] for card in cards)

    if cash_types:
        wallets_set.extend([f"cash - {cash.id}", cash] for cash in cash_types)

    if crypto:
        wallets_set.extend([f"crypto - {crypto.id}", crypto] for crypto in crypto)

    if request.POST.get("wallet_choice"):
        wallets_set, error, income, outcome = process_wallet_post(request, wallets_set, accountancy)

    context = {
        "wallets": wallets_set,
        "current_balance": wallets_set[0][1].balance if not isinstance(wallets_set[0][1], str) else 0,
        "Income": income,
        "Outcome": outcome,
        "error": error,
    }

    return render(request, "manager/index.html", context=context)


def process_wallet_post(
    request: WSGIRequest, wallets_set: list[list[str | Card | Cash | Cryptocurrency]], accountancy: Manager[Accountancy]
) -> tuple[list[list[str | Card | Cash | Cryptocurrency]], ValidationError | None, float, float]:
    error = None
    wallet_type, wallet_id = request.POST["wallet_choice"].split(" - ")
    q_filter, wallet_obj = wallet_choice(wallet_type, int(wallet_id))

    if ("Outcome" in request.POST or request.POST["Income"] != "none") and request.POST["amount"]:
        amount = float(request.POST["amount"])
        expense = "Outcome" if "Outcome" in request.POST else "Income"

        try:
            wallet_obj = change_wallet_balance(expense, wallet_obj, amount)

            acc_data = {
                "IO": expense[0],
                "IO_type": request.POST[expense],
                "amount": amount,
            }

            if wallet_type == "card":
                accountancy.create(card=wallet_obj, **acc_data)
            elif wallet_type == "cash":
                accountancy.create(cash=wallet_obj, **acc_data)
            elif wallet_type == "crypto":
                accountancy.create(cryptocurrency=wallet_obj, **acc_data)
            wallet_obj.save()

        except ValidationError as ve:
            error = ve

    # Move selected wallet at the top
    for wallet_index, wallet in enumerate(wallets_set):
        if wallet[0] == request.POST["wallet_choice"]:
            wallets_set.insert(0, wallets_set.pop(wallet_index))
            wallets_set[0][1] = wallet_obj
            break

    # Get monthly incomes and outcomes
    income = monthly_financial_turnover(q_filter, "I")
    outcome = monthly_financial_turnover(q_filter, "O")

    return wallets_set, error, income, outcome


class MonthlyAccountancyList(LoginRequiredMixin, generic.ListView):
    model: type[Accountancy] = Accountancy  # type: ignore[reportIncompatibleVariableOverride]
    template_name = "manager/monthly_accountancy_list.html"
    paginate_by = 10

    def get_queryset(self) -> QuerySet:
        user_id = self.request.user.id  # type: ignore[reportAttributeAccessIssue]

        # Get month expenses
        self.queryset = cast(
            "QuerySet",
            self.model.objects.filter(Q(card__user=user_id) | Q(cash__user=user_id) | Q(cryptocurrency__user=user_id))
            .annotate(
                month=TruncMonth("datetime"),
            )
            .values("month")
            .annotate(
                amount_sum=Round(Sum("amount"), 8),
            )
            .values(
                "card_id",
                "card__bank_name",
                "card__type",
                "card__currency__sign",
                "cash_id",
                "cash__currency__name",
                "cryptocurrency_id",
                "cryptocurrency__name",
                "IO",
                "amount_sum",
                "month",
            )
            .order_by("-month"),
        )

        return self.queryset


class MonthlyAccountancy(LoginRequiredMixin, generic.ListView):
    model: type[Accountancy] = Accountancy  # type: ignore[reportIncompatibleVariableOverride]
    template_name = "manager/monthly_accountancy.html"
    paginate_by = 10

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        io_type = self.request.GET.get("IO_type", "")
        context["search_form"] = AccountancySearchForm(initial={"IO_type": io_type})

        return context

    def get_queryset(self) -> QuerySet:
        details = self.request.resolver_match.kwargs  # type: ignore[reportOptionalMemberAccess]
        q_filter, _ = wallet_choice(details["wallet"], details["wallet_id"])

        # Get accountancy per specific month & year
        self.queryset = cast(
            "QuerySet",
            self.model.objects.filter(
                q_filter & Q(datetime__month=details["month"]) & Q(datetime__year=details["year"])
            )
            .order_by("-datetime")
            .values("id", "IO", "IO_type", "amount", "datetime"),
        )

        form = AccountancySearchForm(self.request.GET)
        if form.is_valid():
            return self.queryset.filter(IO_type__icontains=form.cleaned_data["IO_type"])

        return self.queryset


class AccountancyUpdate(LoginRequiredMixin, generic.UpdateView):
    model = Accountancy
    form_class = AccountancyForm
    template_name = "manager/accountancy_form.html"
    success_url = reverse_lazy("manager:monthly-accountancy-list")


class AccountancyDelete(LoginRequiredMixin, generic.DeleteView):
    model = Accountancy
    success_url = reverse_lazy("manager:monthly-accountancy-list")
