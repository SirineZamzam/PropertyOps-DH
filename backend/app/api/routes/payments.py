from datetime import (
    date,
    datetime,
    timezone,
)
import logging
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from stripe import SignatureVerificationError

from app.api.dependencies import (
    require_tenant,
)
from app.core.config import settings
from app.db.session import get_db
from app.models.lease import Lease
from app.models.payment import (
    Payment,
    PaymentStatus,
)
from app.models.rent_obligation import (
    RentObligation,
    RentObligationStatus,
)
from app.models.stripe_event import (
    StripeEvent,
)
from app.models.user import User
from app.schemas.payment import (
    CheckoutSessionResponse,
)
from app.services.stripe_service import (
    amount_to_cents,
    create_checkout_session,
    get_stripe_client,
)

router = APIRouter()

logger = logging.getLogger(__name__)


class TenantRentObligationRead(
    BaseModel
):
    id: int
    lease_id: int
    amount: float
    due_date: date
    status: RentObligationStatus

    model_config = {
        "from_attributes": True
    }


def get_tenant_obligation(
    db: Session,
    tenant_id: int,
    obligation_id: int,
) -> RentObligation:
    obligation = db.scalar(
        select(
            RentObligation
        )
        .join(
            Lease,
            RentObligation.lease_id
            == Lease.id,
        )
        .where(
            RentObligation.id
            == obligation_id,

            Lease.tenant_user_id
            == tenant_id,
        )
    )

    if obligation is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail=(
                "Rent obligation not found."
            ),
        )

    return obligation


@router.get(
    "/tenant/homes/{lease_id}/"
    "rent-obligations",

    response_model=list[
        TenantRentObligationRead
    ],
)
def list_tenant_rent_obligations(
    lease_id: int,

    db: Annotated[
        Session,
        Depends(get_db),
    ],

    tenant: Annotated[
        User,
        Depends(require_tenant),
    ],
):
    lease = db.scalar(
        select(Lease).where(
            Lease.id == lease_id,

            Lease.tenant_user_id
            == tenant.id,
        )
    )

    if lease is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Lease not found."
            ),
        )

    obligations = db.scalars(
        select(
            RentObligation
        )
        .where(
            RentObligation.lease_id
            == lease.id
        )
        .order_by(
            RentObligation
            .due_date.desc()
        )
    ).all()

    return list(obligations)


@router.post(
    "/tenant/rent-obligations/"
    "{obligation_id}/checkout",

    response_model=(
        CheckoutSessionResponse
    ),
)
def create_rent_checkout(
    obligation_id: int,

    db: Annotated[
        Session,
        Depends(get_db),
    ],

    tenant: Annotated[
        User,
        Depends(require_tenant),
    ],
):
    obligation = (
        get_tenant_obligation(
            db,
            tenant.id,
            obligation_id,
        )
    )

    if (
        obligation.status
        != RentObligationStatus.PENDING
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail=(
                "Only pending rent "
                "obligations can be paid."
            ),
        )

    payment = Payment(
        rent_obligation_id=(
            obligation.id
        ),

        tenant_user_id=(
            tenant.id
        ),

        amount=(
            obligation.amount
        ),

        currency=(
            settings.stripe_currency
        ),

        status=(
            PaymentStatus.PENDING
        ),
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    try:
        session = (
            create_checkout_session(
                payment=payment,
                obligation=obligation,
                tenant=tenant,
            )
        )

    except Exception:
        payment.status = (
            PaymentStatus.FAILED
        )

        db.commit()

        raise HTTPException(
            status_code=(
                status.HTTP_502_BAD_GATEWAY
            ),
            detail=(
                "Unable to start Stripe "
                "Checkout. Please try again."
            ),
        )

    if not session.url:
        payment.status = (
            PaymentStatus.FAILED
        )

        db.commit()

        raise HTTPException(
            status_code=(
                status.HTTP_502_BAD_GATEWAY
            ),
            detail=(
                "Stripe did not return "
                "a checkout URL."
            ),
        )

    payment.stripe_checkout_session_id = (
        session.id
    )

    payment.status = (
        PaymentStatus.PROCESSING
    )

    db.commit()

    return CheckoutSessionResponse(
        payment_id=payment.id,
        checkout_url=session.url,
    )


@router.post(
    "/stripe/webhook",
)
async def stripe_webhook(
    request: Request,

    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    if not settings.stripe_webhook_secret:
        logger.error(
            "Stripe webhook secret is not configured."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Stripe webhook secret "
                "is not configured."
            ),
        )

    payload = await request.body()

    signature = request.headers.get(
        "stripe-signature"
    )

    if not signature:
        raise HTTPException(
            status_code=400,
            detail=(
                "Missing Stripe signature."
            ),
        )

    try:
        client = get_stripe_client()

        event = client.construct_event(
            payload,
            signature,
            settings.stripe_webhook_secret,
        )

    except ValueError as exc:
        logger.warning(
            "Invalid Stripe payload: %s",
            exc,
        )

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid Stripe payload."
            ),
        ) from exc

    except SignatureVerificationError as exc:
        logger.warning(
            "Invalid Stripe signature: %s",
            exc,
        )

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid Stripe signature."
            ),
        ) from exc

    event_id = event["id"]
    event_type = event["type"]

    logger.info(
        "Stripe webhook verified: %s %s",
        event_id,
        event_type,
    )

    try:
        # -------------------------
        # IDEMPOTENCY CHECK
        # -------------------------

        existing_event = db.scalar(
            select(
                StripeEvent
            ).where(
                StripeEvent.stripe_event_id
                == event_id
            )
        )

        if existing_event:
            logger.info(
                "Ignoring duplicate Stripe event: %s",
                event_id,
            )

            return {
                "received": True,
                "duplicate": True,
            }

        event_object = (
            event["data"]["object"]
            .to_dict()
        )

        # -------------------------
        # CHECKOUT COMPLETED
        # -------------------------

        if (
            event_type
            == "checkout.session.completed"
        ):
            metadata = (
                event_object.get(
                    "metadata",
                    {},
                )
            )

            payment_id = metadata.get(
                "payment_id"
            )

            logger.info(
                "Checkout completed. "
                "Payment metadata ID: %s",
                payment_id,
            )

            if payment_id:
                payment = db.get(
                    Payment,
                    int(payment_id),
                )

                if payment is None:
                    logger.warning(
                        "Payment %s was not found.",
                        payment_id,
                    )

                else:
                    if (
                        payment
                        .stripe_checkout_session_id
                        != event_object.get(
                            "id"
                        )
                    ):
                        raise HTTPException(
                            status_code=400,
                            detail=(
                                "Checkout session "
                                "does not match payment."
                            ),
                        )

                    expected_amount = (
                        amount_to_cents(
                            payment.amount
                        )
                    )

                    stripe_amount = (
                        event_object.get(
                            "amount_total"
                        )
                    )

                    stripe_currency = (
                        event_object.get(
                            "currency"
                        )
                    )

                    logger.info(
                        "Amount check: "
                        "expected=%s stripe=%s "
                        "currency=%s",
                        expected_amount,
                        stripe_amount,
                        stripe_currency,
                    )

                    if (
                        stripe_amount
                        != expected_amount
                    ):
                        raise HTTPException(
                            status_code=400,
                            detail=(
                                "Stripe amount does "
                                "not match payment."
                            ),
                        )

                    if (
                        stripe_currency
                        != payment.currency.lower()
                    ):
                        raise HTTPException(
                            status_code=400,
                            detail=(
                                "Stripe currency does "
                                "not match payment."
                            ),
                        )

                    if (
                        event_object.get(
                            "payment_status"
                        )
                        == "paid"
                    ):
                        logger.info(
                            "Marking payment %s PAID.",
                            payment.id,
                        )

                        payment.status = (
                            PaymentStatus.PAID
                        )

                        payment.stripe_payment_intent_id = (
                            event_object.get(
                                "payment_intent"
                            )
                        )

                        payment.paid_at = (
                            datetime.now(
                                timezone.utc
                            )
                        )

                        obligation = db.get(
                            RentObligation,
                            payment.rent_obligation_id,
                        )

                        if obligation is None:
                            raise RuntimeError(
                                "Rent obligation "
                                f"{payment.rent_obligation_id} "
                                "was not found."
                            )

                        obligation.status = (
                            RentObligationStatus.PAID
                        )

        # -------------------------
        # CHECKOUT EXPIRED
        # -------------------------

        elif (
            event_type
            == "checkout.session.expired"
        ):
            metadata = event_object.get(
                "metadata",
                {},
            )

            payment_id = metadata.get(
                "payment_id"
            )

            if payment_id:
                payment = db.get(
                    Payment,
                    int(payment_id),
                )

                if (
                    payment is not None
                    and payment.status
                    != PaymentStatus.PAID
                ):
                    payment.status = (
                        PaymentStatus.EXPIRED
                    )

        # -------------------------
        # PAYMENT FAILED
        # -------------------------

        elif (
            event_type
            == "payment_intent.payment_failed"
        ):
            metadata = event_object.get(
                "metadata",
                {},
            )

            payment_id = metadata.get(
                "payment_id"
            )

            if payment_id:
                payment = db.get(
                    Payment,
                    int(payment_id),
                )

                if (
                    payment is not None
                    and payment.status
                    != PaymentStatus.PAID
                ):
                    payment.status = (
                        PaymentStatus.FAILED
                    )

                    payment.stripe_payment_intent_id = (
                        event_object.get(
                            "id"
                        )
                    )

        # -------------------------
        # SAVE PROCESSED EVENT
        # -------------------------

        db.add(
            StripeEvent(
                stripe_event_id=event_id,
                event_type=event_type,
            )
        )

        db.commit()

        logger.info(
            "Stripe event processed successfully: %s",
            event_id,
        )

    except IntegrityError:
        db.rollback()

        logger.info(
            "Duplicate Stripe event caught "
            "by database: %s",
            event_id,
        )

        return {
            "received": True,
            "duplicate": True,
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()

        logger.exception(
            "Stripe webhook processing crashed. "
            "event_id=%s event_type=%s",
            event_id,
            event_type,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Stripe webhook processing failed."
            ),
        ) from exc

    return {
        "received": True,
        "duplicate": False,
    }