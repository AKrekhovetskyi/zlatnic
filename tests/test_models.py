from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.test import TestCase
from faker import Faker

from manager.models import Card, Cash, Cryptocurrency, Currency

if TYPE_CHECKING:
    from django.contrib.auth.models import UserManager

BALANCE = 150.0002

fake = Faker()


class ModelsTest(TestCase):
    def setUp(self) -> None:
        user_manager: UserManager = get_user_model().objects
        self.user = user_manager.create_user(
            username=fake.pystr(),
            password=fake.pystr(),
            first_name="Test",
            last_name="Testovetskyi",
            phone_number="+380000000001",
        )
        self.currency = Currency.objects.create(name="U. S. Dollar", abbreviation="USD", sign="$")
        self.card = Card.objects.create(
            user=self.user, bank_name="Mono", type="Payment card", balance=BALANCE, currency=self.currency
        )
        self.cash = Cash.objects.create(user=self.user, currency=self.currency, balance=BALANCE)
        self.crypto = Cryptocurrency.objects.create(user=self.user, name="BitCoin")

        return super().setUp()

    def test_currency_str(self) -> None:
        self.assertEqual(str(self.currency), f"{self.currency.name} ({self.currency.abbreviation})")

    def test_card_str(self) -> None:
        self.assertEqual(
            str(self.card),
            f"Card: {self.card.bank_name} - {self.card.type} - {self.card.balance} {self.card.currency.sign}",
        )

    def test_card_clean(self) -> None:
        self.assertEqual(self.card.balance, round(BALANCE, 2))

    def test_cash_str(self) -> None:
        self.assertEqual(
            str(self.cash), f"Cash - {self.cash.balance} {self.cash.currency.sign} ({self.currency.abbreviation})"
        )

    def test_cash_clean(self) -> None:
        self.assertEqual(self.cash.balance, round(BALANCE, 2))

    def test_cryptocurrency_str(self) -> None:
        self.assertEqual(str(self.crypto), f"Cryptocurrency: {self.crypto.name} - {self.crypto.balance}")
