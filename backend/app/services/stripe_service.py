import stripe

from app.core.config import settings


def configure_stripe() -> None:
    if not settings.stripe_secret_key:
        return

    stripe.api_key = (
        settings.stripe_secret_key
    )