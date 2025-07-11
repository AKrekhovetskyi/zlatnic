from decimal import Decimal
from typing import Any, ClassVar

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class Currency(models.Model):
    name = models.CharField(max_length=50, unique=True)
    abbreviation = models.CharField(max_length=5)
    sign = models.CharField(max_length=5)

    def __str__(self) -> str:
        return f"{self.name} ({self.abbreviation})"


class Card(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="cards")
    bank_name = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    balance = models.FloatField(default=0.0)
    currency = models.ForeignKey(Currency, on_delete=models.RESTRICT, related_name="cards")

    class Meta:
        ordering: ClassVar[list[str]] = ["bank_name"]
        constraints: ClassVar[list[models.UniqueConstraint | models.CheckConstraint]] = [
            models.UniqueConstraint(fields=("user", "bank_name", "type"), name="unique_user_cards"),
            models.CheckConstraint(condition=Q(balance__gte=0), name="positive_card_balance"),
        ]

    def __str__(self) -> str:
        return f"Card: {self.bank_name} - {self.type} - {self.balance} {self.currency.sign}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.balance = round(self.balance, 2)
        return super().save(*args, **kwargs)


class Cash(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="cash")
    currency = models.ForeignKey(Currency, on_delete=models.RESTRICT, related_name="cash")
    balance = models.FloatField(default=0.0)

    class Meta:
        verbose_name = "cash"
        verbose_name_plural = "cash"
        constraints: ClassVar[list[models.UniqueConstraint | models.CheckConstraint]] = [
            models.UniqueConstraint(fields=("user", "currency"), name="unique_user_cash"),
            models.CheckConstraint(condition=Q(balance__gte=0), name="positive_cash_balance"),
        ]

    def __str__(self) -> str:
        return f"Cash - {self.balance} {self.currency.sign} ({self.currency.abbreviation})"

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.balance = round(self.balance, 2)
        return super().save(*args, **kwargs)


class Cryptocurrency(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="cryptocurrencies")
    name = models.CharField(max_length=50)
    balance = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal("0.0"))

    class Meta:
        ordering: ClassVar[list[str]] = ["name"]
        constraints: ClassVar[list[models.UniqueConstraint | models.CheckConstraint]] = [
            models.UniqueConstraint(fields=("user", "name"), name="unique_user_cryptocurrencies"),
            models.CheckConstraint(condition=Q(balance__gte=0), name="positive_cryptocurrency_balance"),
        ]

    def __str__(self) -> str:
        return f"Cryptocurrency: {self.name} - {self.balance}"


class Accountancy(models.Model):
    INCOME = "I"
    OUTCOME = "O"
    IN_OUT_COME: ClassVar[dict[str, str]] = {INCOME: "Income", OUTCOME: "Outcome"}
    RELATED_NAME = "accountancy"

    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name=RELATED_NAME, null=True, blank=True)
    cash = models.ForeignKey(Cash, on_delete=models.CASCADE, related_name=RELATED_NAME, null=True, blank=True)
    cryptocurrency = models.ForeignKey(
        Cryptocurrency, on_delete=models.CASCADE, related_name=RELATED_NAME, null=True, blank=True
    )
    IO = models.CharField(max_length=1, choices=IN_OUT_COME, default=OUTCOME)
    IO_type = models.CharField(max_length=50)
    amount = models.FloatField()
    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar[list[str]] = ["-datetime"]
        constraints: ClassVar[list[models.CheckConstraint]] = [
            models.CheckConstraint(
                condition=(Q(card__isnull=False) & Q(cash__isnull=True) & Q(cryptocurrency__isnull=True))
                | (Q(card__isnull=True) & Q(cash__isnull=False) & Q(cryptocurrency__isnull=True))
                | (Q(card__isnull=True) & Q(cash__isnull=True) & Q(cryptocurrency__isnull=False)),
                name="only_one_wallet",
            ),
            models.CheckConstraint(condition=Q(amount__gte=0), name="positive_amount"),
        ]

    def __str__(self) -> str:
        return f"Accountancy: {self.IO}, {self.IO_type}, {self.amount}, {self.datetime}"

    def clean(self) -> None:
        if self.card and self.cash and self.cryptocurrency:
            raise ValidationError("Only one of the wallet fields can be set.")
        if self.amount < 0:
            raise ValidationError("Amount can't be negative.")
