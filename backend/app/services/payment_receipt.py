from datetime import (
    datetime,
    timezone,
)
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.graphics.shapes import (
    Drawing,
    Line,
    Rect,
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.models.building import Building
from app.models.payment import Payment
from app.models.property import Property
from app.models.rent_obligation import RentObligation
from app.models.unit import Unit
from app.models.user import User


BRAND = colors.HexColor("#17324B")
ACCENT = colors.HexColor("#519DC4")
SOFT = colors.HexColor("#EAF7FD")
MUTED = colors.HexColor("#607588")
BORDER = colors.HexColor("#D9E6EC")


def safe(
    value: object | None,
) -> str:
    if value is None:
        return "—"

    text = str(value).strip()

    return escape(
        text or "—"
    )


def full_name(
    user: User,
) -> str:
    name = " ".join(
        part
        for part in [
            user.first_name,
            user.last_name,
        ]
        if part
    ).strip()

    return name or user.email


def building_mark() -> Drawing:
    drawing = Drawing(
        38,
        38,
    )

    drawing.add(
        Rect(
            0,
            0,
            38,
            38,
            rx=8,
            ry=8,
            fillColor=BRAND,
            strokeColor=BRAND,
        )
    )

    drawing.add(
        Rect(
            11,
            8,
            16,
            23,
            fillColor=None,
            strokeColor=colors.white,
            strokeWidth=1.6,
        )
    )

    for x in (
        15,
        23,
    ):
        drawing.add(
            Line(
                x,
                13,
                x,
                26,
                strokeColor=colors.white,
                strokeWidth=1.2,
            )
        )

    for y in (
        17,
        23,
    ):
        drawing.add(
            Line(
                12,
                y,
                26,
                y,
                strokeColor=colors.white,
                strokeWidth=1.2,
            )
        )

    return drawing


def build_payment_receipt(
    *,
    payment: Payment,
    obligation: RentObligation,
    tenant: User,
    owner: User,
    property_record: Property,
    building: Building,
    unit: Unit,
) -> bytes:
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=(
            "PropertyOps Rent "
            f"Receipt {payment.id}"
        ),
    )

    styles = getSampleStyleSheet()

    brand_title = ParagraphStyle(
        "BrandTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=19,
        leading=22,
        textColor=BRAND,
        spaceAfter=0,
    )

    subtitle = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=11,
        textColor=MUTED,
    )

    receipt_title = ParagraphStyle(
        "ReceiptTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=20,
        textColor=BRAND,
        alignment=TA_RIGHT,
    )

    section_title = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=BRAND,
        spaceBefore=10,
        spaceAfter=6,
    )

    value_style = ParagraphStyle(
        "Value",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=BRAND,
    )

    label_style = ParagraphStyle(
        "Label",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=MUTED,
    )

    story = []

    receipt_number = (
        f"PO-RNT-{payment.id:06d}"
    )

    header = Table(
        [
            [
                building_mark(),
                Paragraph(
                    (
                        "<b>PropertyOps</b><br/>"
                        "<font size='8' "
                        "color='#607588'>"
                        "Property Operations"
                        "</font>"
                    ),
                    brand_title,
                ),
                Paragraph(
                    (
                        "<b>RENT RECEIPT</b><br/>"
                        f"<font size='9'>"
                        f"{receipt_number}"
                        "</font>"
                    ),
                    receipt_title,
                ),
            ]
        ],
        colWidths=[
            14 * mm,
            92 * mm,
            66 * mm,
        ],
        vAlign="MIDDLE",
    )

    header.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
            ]
        )
    )

    story.append(header)
    story.append(
        Spacer(
            1,
            7 * mm,
        )
    )

    paid_at = (
        payment.paid_at
        or payment.updated_at
        or payment.created_at
    )

    generated_at = datetime.now(
        timezone.utc
    )

    summary = Table(
        [
            [
                Paragraph(
                    "Amount paid",
                    label_style,
                ),
                Paragraph(
                    "Payment method",
                    label_style,
                ),
                Paragraph(
                    "Paid date",
                    label_style,
                ),
            ],
            [
                Paragraph(
                    (
                        f"<b>{safe(payment.currency.upper())} "
                        f"{payment.amount:.2f}</b>"
                    ),
                    value_style,
                ),
                Paragraph(
                    safe(
                        payment.payment_method.value
                    ),
                    value_style,
                ),
                Paragraph(
                    paid_at.strftime(
                        "%d %b %Y"
                    ),
                    value_style,
                ),
            ],
        ],
        colWidths=[
            58 * mm,
            58 * mm,
            58 * mm,
        ],
    )

    summary.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    SOFT,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    BORDER,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.35,
                    BORDER,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
            ]
        )
    )

    story.append(summary)

    def detail_table(
        rows: list[
            tuple[str, object | None]
        ],
    ):
        data = [
            [
                Paragraph(
                    safe(label),
                    label_style,
                ),
                Paragraph(
                    safe(value),
                    value_style,
                ),
            ]
            for (
                label,
                value,
            ) in rows
        ]

        table = Table(
            data,
            colWidths=[
                44 * mm,
                130 * mm,
            ],
            hAlign="LEFT",
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "LINEBELOW",
                        (0, 0),
                        (-1, -2),
                        0.3,
                        BORDER,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        0,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )

        return table

    story.append(
        Paragraph(
            "Tenant",
            section_title,
        )
    )
    story.append(
        detail_table(
            [
                (
                    "Name",
                    full_name(tenant),
                ),
                (
                    "Email",
                    tenant.email,
                ),
                (
                    "Phone",
                    tenant.phone_number,
                ),
            ]
        )
    )

    story.append(
        Paragraph(
            "Property",
            section_title,
        )
    )

    address = ", ".join(
        item
        for item in [
            property_record.address,
            property_record.city,
            property_record.country,
        ]
        if item
    )

    story.append(
        detail_table(
            [
                (
                    "Property",
                    property_record.name,
                ),
                (
                    "Address",
                    address,
                ),
                (
                    "Building",
                    building.name,
                ),
                (
                    "Unit",
                    unit.unit_number,
                ),
                (
                    "Rent due date",
                    obligation.due_date.strftime(
                        "%d %b %Y"
                    ),
                ),
            ]
        )
    )

    story.append(
        Paragraph(
            "Owner",
            section_title,
        )
    )
    story.append(
        detail_table(
            [
                (
                    "Name",
                    full_name(owner),
                ),
                (
                    "Email",
                    owner.email,
                ),
                (
                    "Phone",
                    owner.phone_number,
                ),
            ]
        )
    )

    payment_rows: list[
        tuple[str, object | None]
    ] = [
        (
            "Receipt reference",
            receipt_number,
        ),
        (
            "Payment ID",
            payment.id,
        ),
        (
            "Payment method",
            payment.payment_method.value,
        ),
    ]

    if (
        payment.stripe_payment_intent_id
    ):
        payment_rows.append(
            (
                "Stripe reference",
                payment.stripe_payment_intent_id,
            )
        )

    if payment.manual_note:
        payment_rows.append(
            (
                "Note",
                payment.manual_note,
            )
        )

    story.append(
        Paragraph(
            "Payment details",
            section_title,
        )
    )
    story.append(
        detail_table(
            payment_rows
        )
    )

    story.append(
        Spacer(
            1,
            9 * mm,
        )
    )

    footer = Paragraph(
        (
            "Generated by PropertyOps on "
            f"{generated_at.strftime('%d %b %Y %H:%M UTC')}. "
            "This receipt records a payment marked PAID "
            "in the PropertyOps system."
        ),
        subtitle,
    )

    story.append(footer)

    document.build(story)

    return buffer.getvalue()
