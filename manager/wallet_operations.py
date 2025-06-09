from datetime import UTC, datetime

from django.core.exceptions import ValidationError
from django.db.models import Model, Q, Sum

from manager.models import Accountancy, Card, Cash, Cryptocurrency


def wallet_data_parse(request: dict) -> tuple[str, int]:
    (
        wallet_type,
        integer,
    ) = request["wallet_choice"].split(" - ")

    return wallet_type, integer


def wallet_choice(wallet_type: str, wallet_id: int) -> tuple[Q, Model]:
    q_filter, wallet_obj = Q(), None

    if wallet_type == "card":
        q_filter = Q(card_id=wallet_id)
        wallet_obj = Card.objects.get(id=wallet_id)
    elif wallet_type == "cash":
        q_filter = Q(cash_id=wallet_id)
        wallet_obj = Cash.objects.get(id=wallet_id)
    elif wallet_type == "crypto":
        q_filter = Q(cryptocurrency_id=wallet_id)
        wallet_obj = Cryptocurrency.objects.get(id=wallet_id)

    return q_filter, wallet_obj


def monthly_financial_turnover(q_filter: Q, turnover_type: str) -> int:
    turnover = Accountancy.objects.filter(
        q_filter & Q(IO=turnover_type) & Q(datetime__month=datetime.now(UTC).month)
    ).aggregate(Sum("amount"))
    if not turnover or not turnover.get("amount__sum"):
        return 0
    return round(turnover["amount__sum"], 8)


def change_wallet_balance(expense: str, wallet_obj: Model, amount: float) -> Model:
    if expense in ("Outcome", "O") and wallet_obj.balance < amount:
        raise ValidationError("There's too small amount of money on the balance")
    if expense in ("Outcome", "O"):
        wallet_obj.balance = float(wallet_obj.balance) - amount
    elif expense in ("Income", "I"):
        wallet_obj.balance = float(wallet_obj.balance) + amount

    return wallet_obj
