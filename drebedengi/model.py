""" Drebedengi data model & API dictionaries """

from datetime import datetime
from enum import IntEnum

from attrs import define, field
from attrs.converters import optional, to_bool


def _xml_dttm_str_to_datetime(xml_str: str | datetime) -> datetime:
    """Converts XML datetime string to datetime object."""
    if isinstance(xml_str, datetime):
        return xml_str

    return datetime.strptime(xml_str, "%Y-%m-%d %H:%M:%S")


def _xml_timestamp_to_datetime(xml_str: str | datetime) -> datetime:
    """Converts XML timestamp value to datetime object."""
    if isinstance(xml_str, datetime):
        return xml_str

    return datetime.fromtimestamp(float(xml_str))


class ReportPeriod(IntEnum):
    CUSTOM_PERIOD = 0
    THIS_MONTH = 1
    TODAY = 7
    LAST_MONTH = 2
    THIS_QUART = 3
    THIS_YEAR = 4
    LAST_YEAR = 5
    ALL_TIME = 6
    LAST_20_RECORD = 8


class ReportGrouping(IntEnum):
    NONE = 1
    BY_INCOME_SOURCE = 2
    BY_EXPENSE_CATEGORY = 3


class ReportFilterType(IntEnum):
    NONE = 0
    SELECTED_ONLY = 1
    EXCEPT_SELECTED = 2


class TransactionType(IntEnum):
    INCOME = 2
    EXPENSE = 3
    TRANSFER = 4
    EXCHANGE = 5
    ANY = 6


def _transaction_type_from_str(transaction_type_str: str) -> TransactionType:
    """Converts transaction type string to TransactionType enum."""
    return TransactionType(int(transaction_type_str))


@define
class Transaction:
    """Drebedengi transaction (aka Record) model."""

    id: int = field(converter=int)
    budget_object_id: int = field(converter=int)
    user_nuid: int = field(converter=int)
    budget_family_id: int = field(converter=int)
    # FIX THIS: change to a relevant name
    is_duty: bool = field(converter=to_bool, metadata={"xml": {"name": "is_duty"}})
    operation_date: datetime = field(converter=_xml_dttm_str_to_datetime)
    comment: str = field(converter=str)
    currency_id: int = field(converter=int)
    operation_type: TransactionType = field(converter=_transaction_type_from_str)
    account_id: int = field(converter=int, metadata={"xml": {"name": "place_id"}})
    amount: int = field(converter=int, metadata={"xml": {"name": "sum"}})
    """ Transaction amount in the original currency """
    oper_utc_timestamp: datetime | None = field(
        converter=optional(_xml_timestamp_to_datetime),
        metadata={"xml": {"name": "oper_timestamp"}},
        default=None,
    )
    group_id: int | None = field(converter=optional(int), default=None)
