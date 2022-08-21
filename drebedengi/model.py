""" Drebedengi data model & API dictionaries module """

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
    """Report period enum. Used in get_transactions API to filter by date.

    Attributes:
        CUSTOM_PERIOD (int): 0
        THIS_MONTH (int): 1
        TODAY (int): 7
        LAST_MONTH (int): 2
        THIS_QUART (int): 3
        THIS_YEAR (int): 4
        LAST_YEAR (int): 5
        ALL_TIME (int): 6
        LAST_20_RECORD (int): 8
    """

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
    """Report grouping enum. Used in get_transactions API to configure aggregated report.

    Attributes:
        NONE (int): 1
        BY_INCOME_SOURCE (int): 2
        BY_EXPENSE_CATEGORY (int): 3
    """

    NONE = 1
    BY_INCOME_SOURCE = 2
    BY_EXPENSE_CATEGORY = 3


class ReportFilterType(IntEnum):
    """Report filter type enum. Used in get_transactions API to configure categories, tags and other filters.

    Attributes:
        NONE (int): 0
        SELECTED_ONLY (int): 1
        EXCEPT_SELECTED (int): 2
    """

    NONE = 0
    SELECTED_ONLY = 1
    EXCEPT_SELECTED = 2


class TransactionType(IntEnum):
    """Enum of possible transaction types.

    Attributes:
        INCOME (int): 2
        EXPENSE (int): 3
        TRANSFER (int): 4
        EXCHANGE (int): 5
        ANY (int): 6
    """

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
    """Drebedengi transaction (aka Record) model.

    Attributes:
        id (int): transaction id
        budget_object_id: (int) For expenses - expense category; for incomes - income source; for others TBC.
        user_nuid: (int) User id.
        budget_family_id: (int) Family id for multi-user mode.
        is_loan_transfer: (bool) = Makrs trabsfer transactions that went to a "loan" account.
        operation_date: (datetime) Operation date in user set timezone.
        currency_id: (int) Transaction currency id.
        operation_type: (TransactionType) Transaction type.
        account_id: (int) Account id.
        amount: (int) Transaction amount in the original currency multiplied by 100
        comment: (str | None) Transaction comment. May be empty
        oper_utc_timestamp (datetime): Operation date in UTC.
        group_id (int): Group id if this transaction is part of a group.
    """

    id: int = field(converter=int)
    budget_object_id: int = field(converter=int)
    user_nuid: int = field(converter=int)
    budget_family_id: int = field(converter=int)
    is_loan_transfer: bool = field(converter=to_bool, metadata={"xml": {"name": "is_duty"}})
    operation_date: datetime = field(converter=_xml_dttm_str_to_datetime)
    currency_id: int = field(converter=int)
    operation_type: TransactionType = field(converter=_transaction_type_from_str)
    account_id: int = field(converter=int, metadata={"xml": {"name": "place_id"}})
    amount: int = field(converter=int, metadata={"xml": {"name": "sum"}})
    comment: str | None = field(converter=str, default=None)
    oper_utc_timestamp: datetime | None = field(
        converter=optional(_xml_timestamp_to_datetime),
        metadata={"xml": {"name": "oper_timestamp"}},
        default=None,
    )
    group_id: int | None = field(converter=optional(int), default=None)


class ObjectType(IntEnum):
    """Enum of possible object types. Used in `ChangeRecord` and other models.

    Attributes:
        TRANSACTION (int): 1
        INCOME_SOURCE (int): 2
        EXPENSE_CATEGORY (int): 3
        ACCOUNT (int): 4
        CURRENCY (int): 5
        BUDGET_TAGS (int): 6
        BUDGET_ACCUM (int): 7
        BUDGET_ACCUM_ORDER (int): 8
    """

    TRANSACTION = 1
    INCOME_SOURCE = 2
    EXPENSE_CATEGORY = 3
    ACCOUNT = 4
    CURRENCY = 5
    BUDGET_TAGS = 6  # fIXME: proper name
    BUDGET_ACCUM = 7  # fIXME: proper name
    BUDGET_ACCUM_ORDER = 8  # fIXME: proper name


def _object_type_from_str(object_type_str: str) -> ObjectType:
    """Converts Object type string to ObjectType enum."""
    return ObjectType(int(object_type_str))


class ActionType(IntEnum):
    """Enum of possible change action types. Used in `ChangeRecord` model.

    Attributes:
        CREATE (int): 1
        UPDATE (int): 2
        DELETE (int): 3
    """

    CREATE = 1
    UPDATE = 2
    DELETE = 3


def _action_type_from_str(action_type_str: str) -> ActionType:
    """Converts action type string to ActionType enum."""
    return ActionType(int(action_type_str))


@define
class ChangeRecord:
    """Drebedengi change record model.

    Attributes:
        revision_id (int): Revision id.
        action_type (ActionType): Action type (update, create, delete).
        change_object_type (ObjectType): changed object type.
        object_id (int): changed object type id.
        date (datetime): change date in user set timezone.
    """

    revision_id: int = field(converter=int, metadata={"xml": {"name": "revision"}})
    action_type: ActionType = field(
        converter=_action_type_from_str, metadata={"xml": {"name": "action_id"}}
    )
    change_object_type: ObjectType = field(
        converter=_object_type_from_str, metadata={"xml": {"name": "object_type_id"}}
    )
    object_id: int = field(converter=int)
    date: datetime = field(converter=_xml_dttm_str_to_datetime)


@define
class ExpenseCategory:
    """Drebedengi expense category model.

    Attributes:
        id (int): id is a unique identifier for the expense category.
        parent_id (int): parent_id is the id of the parent expense category. If the expense category has no parent, parent_id is -1.
        budget_family_id (int): User family ID (for multiuser mode)
        object_type (ObjectType): Always ObjectType.EXPENSE_CATEGORY
        name (str): Name of the expense category.
        is_hidden (bool): True if the expense category is hidden.
        sort (int): Sort order of the expense category.
    """

    id: int = field(converter=int)
    parent_id: int = field(converter=int)
    budget_family_id: int = field(converter=int)
    object_type: ObjectType = field(
        converter=_object_type_from_str, metadata={"xml": {"name": "type"}}
    )
    name: str = field(converter=str)
    is_hidden: bool = field(converter=to_bool)
    sort: int = field(converter=int)


@define
class IncomeSource:
    """Drebedengi income source model.

    Attributes:
        id (int): id is a unique identifier for the income source.
        parent_id (int): parent_id is the id of the parent income source. If the income source has no parent, parent_id is -1.
        budget_family_id (int): User family ID (for multiuser mode)
        object_type (ObjectType): Always ObjectType.INCOME_SOURCE
        name (str): Name of the income source.
        is_hidden (bool): True if the income source is hidden.
        sort (int): Sort order of the income source.
    """

    id: int = field(converter=int)
    parent_id: int = field(converter=int)
    budget_family_id: int = field(converter=int)
    object_type: ObjectType = field(
        converter=_object_type_from_str, metadata={"xml": {"name": "type"}}
    )
    name: str = field(converter=str)
    is_hidden: bool = field(converter=to_bool)
    sort: int = field(converter=int)


@define
class Tag:
    """Drebedengi tag model.

    Attributes:
        id (int): id is a unique identifier for the tag.
        parent_id (int): parent_id is the id of the parent tag. If the tag has no parent, parent_id is -1.
        budget_family_id (int): User family ID (for multiuser mode)
        name (str): Name of the tag.
        is_hidden (bool): True if the tag is hidden.
        is_shared (bool): True if the tag is shared across family account, otherwise it's user only.
        sort (int): Sort order of the tag.
    """

    id: int = field(converter=int)
    parent_id: int = field(converter=int)
    budget_family_id: int = field(converter=int, metadata={"xml": {"name": "family_id"}})
    name: str = field(converter=str)
    is_hidden: bool = field(converter=to_bool)
    is_shared: bool = field(converter=to_bool, metadata={"xml": {"name": "is_family"}})
    sort: int = field(converter=int)


@define
class Currency:
    """Drebedengi currency model.

    Attributes:
        id (int): id is a unique drebedengi internal identifier for the currency.
        user_name (str): A custom currency name assigned by the user.
        currency_code (str): International 3-leet currency code.
        exchange_rate (float): Current exchange rate from the default currency to the currency.
        budget_family_id (int): User family ID (for multiuser mode)
        is_default (bool): True if the currency is set as default.
        is_autoupdate (bool): True if the currency is configured to fecth exchange rate automatically.
        is_hidden (bool): True if the currency is hidden.
    """

    id: int = field(converter=int)
    user_name: str = field(converter=str, metadata={"xml": {"name": "name"}})
    currency_code: str = field(converter=str, metadata={"xml": {"name": "code"}})
    exchange_rate: float = field(converter=float, metadata={"xml": {"name": "course"}})
    budget_family_id: int = field(converter=int, metadata={"xml": {"name": "family_id"}})
    is_default: bool = field(converter=to_bool)
    is_autoupdate: bool = field(converter=to_bool)
    is_hidden: bool = field(converter=to_bool)


@define
class Account:
    """Drebedengi account model.

    Attributes:
        id (int): id is a unique identifier for the account.
        budget_family_id (int): User family ID (for multiuser mode)
        object_type (ObjectType): Always ObjectType.ACCOUNT
        name (str): Account name assigned by the user.
        is_hidden (bool): True if the account is hidden.
        is_autohide (bool): True if the account is configured to hide on zero balance.
        is_loan (bool): True if the account is for loans (both taken and given).
        sort (int): Sort order of the account.
        wallet_user_id (int | None): User Id if account is marked as a personal wallet.
        icon_id (str | None): Account Icon Id.
    """

    id: int = field(converter=int)
    budget_family_id: int = field(converter=int)
    object_type: ObjectType = field(
        converter=_object_type_from_str, metadata={"xml": {"name": "type"}}
    )
    name: str = field(converter=str)
    is_hidden: bool = field(converter=to_bool)
    is_autohide: bool = field(converter=to_bool)
    is_loan: bool = field(converter=to_bool, metadata={"xml": {"name": "is_for_duty"}})
    sort: int = field(converter=int)
    wallet_user_id: int | None = field(
        converter=optional(int), metadata={"xml": {"name": "purse_of_nuid"}}, default=None
    )
    icon_id: str | None = field(default=None)
