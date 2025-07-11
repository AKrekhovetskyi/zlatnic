from django.urls import path

from .views import (
    AccountancyDelete,
    AccountancyUpdate,
    CardCreateView,
    CardDeleteView,
    CardUpdateView,
    CashCreateView,
    CashDeleteView,
    CashUpdateView,
    CryptoCreateView,
    CryptoDeleteView,
    CryptoUpdateView,
    MonthlyAccountancy,
    MonthlyAccountancyList,
    index,
    wallets,
)

urlpatterns = [
    path("wallets/", wallets, name="wallets"),
    path("wallets/card/", CardCreateView.as_view(), name="card-create"),
    path("wallets/card/update/<int:pk>/", CardUpdateView.as_view(), name="card-update"),
    path("wallets/card/delete/<int:pk>/", CardDeleteView.as_view(), name="card-delete"),
    path("wallets/cash/", CashCreateView.as_view(), name="cash-create"),
    path("wallets/cash/update/<int:pk>/", CashUpdateView.as_view(), name="cash-update"),
    path("wallets/cash/delete/<int:pk>/", CashDeleteView.as_view(), name="cash-delete"),
    path("wallets/crypto/", CryptoCreateView.as_view(), name="crypto-create"),
    path(
        "wallets/crypto/update/<int:pk>/",
        CryptoUpdateView.as_view(),
        name="crypto-update",
    ),
    path(
        "wallets/crypto/delete/<int:pk>/",
        CryptoDeleteView.as_view(),
        name="crypto-delete",
    ),
    path("", index, name="index"),
    path(
        "accountancy/",
        MonthlyAccountancyList.as_view(),
        name="monthly-accountancy-list",
    ),
    path(
        "accountancy/<str:wallet>/<int:wallet_id>/<int:month>/<int:year>/",
        MonthlyAccountancy.as_view(),
        name="monthly-accountancy",
    ),
    path(
        "accountancy/update/<int:pk>/",
        AccountancyUpdate.as_view(),
        name="accountancy-update",
    ),
    path(
        "accountancy/delete/<int:pk>/",
        AccountancyDelete.as_view(),
        name="accountancy-delete",
    ),
]

app_name = "manager"
