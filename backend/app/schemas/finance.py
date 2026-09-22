from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class FinancialSeriesPoint(BaseModel):
    label: str
    rent_collected: Decimal
    expenses: Decimal


class FinancialOverviewRead(BaseModel):
    start_date: date
    end_date: date
    bucket: str

    rent_collected: Decimal
    expenses: Decimal
    net_cash_flow: Decimal
    outstanding_rent: Decimal

    series: list[FinancialSeriesPoint]
