import logging
from datetime import datetime

import zeep
from lxml import etree
from requests.models import Response
from zeep.client import Client
from zeep.transports import Transport

from .model import (
    Account,
    ChangeRecord,
    Currency,
    ExpenseCategory,
    IncomeSource,
    ReportFilterType,
    ReportGrouping,
    ReportPeriod,
    Tag,
    Transaction,
    TransactionType,
)
from .utils import generate_xml_array, xmlmap_to_model

from typing import Any, Dict, List

logger = logging.getLogger(__name__)

DREBEDENGI_DEFAULT_SOAP_URL = "https://www.drebedengi.ru/soap/dd.wsdl"
DREBEDENGI_DEFAULT_TIMEOUTS = (60, 300)


class DrebedengiAPIError(Exception):
    """Drebedengi API error class."""

    def __init__(
        self, message: str, status_code: int, response_text: str, fault_code: str | None = None
    ) -> None:
        """Initialize."""
        self.status_code = status_code
        self.response_text = response_text
        self.fault_code = fault_code
        super().__init__(message, fault_code)

    @classmethod
    def check_and_raise(cls, response: Response) -> None:
        """
        Check if response is an API error and immediatelly raise it.
        """
        if not response.ok:
            raise cls("Network error", response.status_code, response.text)

        root = etree.fromstring(response.content)
        fault = root.find(".//{http://schemas.xmlsoap.org/soap/envelope/}Fault")
        if fault is not None:
            raise cls(
                fault.findtext(".//faultstring"),
                response.status_code,
                response.text,
                fault.findtext(".//faultcode"),
            )


class DrebedengiAPI:
    """Drebedengi API Wrapper class."""

    def __init__(
        self,
        api_key: str,
        login: str,
        password: str,
        *,
        strict: bool = True,
        soap_url: str = DREBEDENGI_DEFAULT_SOAP_URL,
        wsdl_timeout: float = DREBEDENGI_DEFAULT_TIMEOUTS[0],
        operation_timeout: float = DREBEDENGI_DEFAULT_TIMEOUTS[1],
    ) -> None:
        """API Wrapper class

        Args:
            api_key (str): api_key (get from drebedengi via support)
            login (str): your login
            password (str): your password
            strict (bool, optional): strict mode - API calls will fail if the returned data doesn't match the model. Defaults to True.
            soap_url (str, optional): Optional alternative SOAP URL. Defaults to DREBEDENGI_DEFAULT_SOAP_URL.
            wsdl_timeout (float, optional): WSDL download timeout. Defaults to 60s.
            operation_timeout (float, optional): Operation timeout. Defaults to 300s.
        """
        self.api_key = api_key
        self.login = login
        self.password = password
        self.soap_url = soap_url
        self.strict = strict
        transport = Transport(timeout=wsdl_timeout, operation_timeout=operation_timeout)
        self.client = Client(soap_url, transport=transport)  # type: ignore

        logger.debug(
            f"Initialized DrebedengiAPI for {login=}. SOAP URL: {self.soap_url}. Strict: {self.strict}"
        )

    def get_transactions(
        self,
        *,
        relative_date: datetime | None = None,
        period_from: datetime | None = None,
        period_to: datetime | None = None,
        account_filter: ReportFilterType = ReportFilterType.NONE,
        account_filter_ids: List[int] | None = None,
        tag_filter: ReportFilterType = ReportFilterType.NONE,
        tag_filter_ids: List[int] | None = None,
        category_filter: ReportFilterType = ReportFilterType.NONE,
        category_filter_ids: List[int] | None = None,
        include_types: TransactionType = TransactionType.ANY,
        convert_to_currency_id: int = 0,
        aggregated: bool = False,
        group_by: ReportGrouping = ReportGrouping.NONE,
        report_period: ReportPeriod = ReportPeriod.LAST_20_RECORD,
        id_list: List[int] | None = None,
    ) -> List[Transaction]:
        """
        Implements getRecordList API

        Original wsdl description:
            Retrievs record list (array of arrays) or report table by parameters; [params] => array of following parameters: 'is_report' [true|false (no default)] - retrievs data for report only or full records (waste, incomes, moves, changes) for export; 'relative_date' [YYYY-MM-DD (NOW by default)] - all data will be retrieved relative to this value, according to 'r_period' value; 'period_to', 'period_from' [YYYY-MM-DD] - custom period, if 'r_period' = 0; 'is_show_duty' [true(default)|false] - whether or not include duty record; 'r_period' [custom period = 0, this month = 1, today = 7, last month = 2, this quart = 3, this year = 4, last year = 5, all time = 6, last 20 record = 8 (default)] - period for which data will be obtained; 'r_what' [income = 2, waste = 3 (default), move = 4, change = 5, all types = 6] - type of data you want to get; 'r_who' [0 (default) - all users, int8 = user ID] - The data of the user to obtain, in the case of multiplayer mode; 'r_how' [show record list by detail = 1 (default), group incomes by source = 2, group wastes by category = 3] - Values 2 and 3 are for 'report' mode only# How to group the result record list; 'r_middle' [No average = 0 (default), Average monthly = 2592000, Average weekly = 604800, Averaged over days = 86400] - How to average the data, if r_how = 2 or 3; 'r_currency' [Original currency = 0 (default), int8 = currency ID] - Convert or not in to given currency; 'r_is_place', 'r_is_tag', 'r_is_category' [Include all = 0 (default), Include only selected = 1, All except selected = 2] - Exclude or include 'r_place', 'r_tag' or 'r_category' respectively; 'r_place', 'r_tag', 'r_category' [Array] - Array of numeric values for place ID, tag ID or category ID respectively; If parameter [idList] is given, it will be treat as ID list of objects to retrieve# this is used for synchronization;
        """

        logger.debug(
            f"Getting transactions with the following params: {relative_date=}, {period_from=}, {period_to=}, {account_filter=}, {account_filter_ids=}, {tag_filter=}, {tag_filter_ids=}, {category_filter=}, {category_filter_ids=}, {include_types=}, {convert_to_currency_id=}, {aggregated=}, {group_by=}, {report_period=}"
        )

        if not aggregated and group_by != ReportGrouping.NONE:
            raise ValueError("group_by can be used only with aggregated=True")

        if account_filter != ReportFilterType.NONE and account_filter_ids is None:
            raise ValueError("account_filter_ids must be set if account_filter is not NONE")

        if tag_filter != ReportFilterType.NONE and tag_filter_ids is None:
            raise ValueError("tag_filter_ids must be set if tag_filter is not NONE")

        if category_filter != ReportFilterType.NONE and category_filter_ids is None:
            raise ValueError("category_filter_ids must be set if category_filter is not NONE")

        pdict: Dict[str, Any] = {
            "r_period": int(report_period),
            "is_report": aggregated,
            "is_show_duty": True,  # this is a bogus param that allows to show or filter out transfers to liability accounts when only expenses are requested
            "r_how": int(group_by),
            "r_what": int(include_types),
            "r_currency": convert_to_currency_id,
            "r_is_place": int(account_filter),
            "r_is_tag": int(tag_filter),
            "r_is_category": int(category_filter),
        }

        if account_filter != ReportFilterType.NONE:
            pdict["r_place"] = account_filter_ids

        if tag_filter != ReportFilterType.NONE:
            pdict["r_tag"] = tag_filter_ids

        if category_filter != ReportFilterType.NONE:
            pdict["r_category"] = category_filter_ids

        if include_types == TransactionType.EXPENSE:
            pdict["is_show_duty"] = False

        if relative_date is None:
            relative_date = datetime.now()

        pdict["relative_date"] = relative_date.strftime("%Y-%m-%d")

        if period_from and period_to:
            pdict["period_from"] = period_from.strftime("%Y-%m-%d")
            pdict["period_to"] = period_to.strftime("%Y-%m-%d")
            pdict["r_period"] = int(ReportPeriod.CUSTOM_PERIOD)
            del pdict["relative_date"]

        params = zeep.helpers.create_xml_soap_map(pdict)  # type: ignore

        if id_list is not None:
            id_list_xml = generate_xml_array(id_list)
        else:
            id_list_xml = zeep.xsd.SkipValue  # type: ignore

        if aggregated:
            raise NotImplementedError("aggregated is not implemented yet")

        client = self.client

        with client.settings(raw_response=True, strict=False):
            result = client.service.getRecordList(
                self.api_key,
                self.login,
                self.password,
                idList=id_list_xml,
                params=params,
            )

            DrebedengiAPIError.check_and_raise(result)

        root = etree.fromstring(result.content)
        items: List[etree.Element] = root.findall(".//getRecordListReturn/item/value")

        return [xmlmap_to_model(item, Transaction, strict=self.strict) for item in items]

    def get_changes(self, *, revision: int) -> List[ChangeRecord]:
        """
        Implements getChangeList API

        Original wsdl description:
            Get all changes (array of arrays) from server relative to given revision: [revision] => the revision of the change, [action_id] => the action of the change '1' - add, '2' - update, '3' - delete'; [object_type_id] => type of the object changed '1' - any record (transction), '2' - income source, '3' - waste category, '4' - place, '5' - currency, '6' - budget_tags, '7' - budget_accum, '8' - budget_accum_order; [object_id] => ID of the object for subsequent calls getRecordList, getCategoryList etc; [date] => the date of the change; Parameter [revision] => int8 number, usually saved on the client from last successfull sync.
        """

        logger.debug(f"Getting changes with the following params: {revision=}")

        client = self.client

        with client.settings(raw_response=True, strict=False):
            result = client.service.getChangeList(
                self.api_key, self.login, self.password, revision=revision
            )

            DrebedengiAPIError.check_and_raise(result)

        root = etree.fromstring(result.content)
        items: List[etree.Element] = root.findall(".//getChangeListReturn/item")

        return [xmlmap_to_model(item, ChangeRecord, strict=self.strict) for item in items]

    def get_expense_categories(
        self,
        *,
        id_list: List[int] | None = None,
    ) -> List[ExpenseCategory]:
        """
        Implements getCategoryList API

        Original wsdl description:
            Retrievs waste category list (array of arrays): [id] => Internal category ID; [parent_id] => For tree structure; [budget_family_id] => User family ID (for multiuser mode); [type] => Type of object, 3 - waste category; [name] => Category name given by user; [is_hidden] => is category hidden in user interface; [sort] => User sort of category tree; If parameter [idList] is given, it will be treat as ID list of objects to retrieve# this is used for synchronization;
        """

        logger.debug(f"Getting categories with the following params: {id_list=}")

        if id_list is not None:
            id_list_xml = generate_xml_array(id_list)
        else:
            id_list_xml = zeep.xsd.SkipValue  # type: ignore

        client = self.client

        with client.settings(raw_response=True, strict=False):
            result = client.service.getCategoryList(
                self.api_key,
                self.login,
                self.password,
                idList=id_list_xml,
            )

            DrebedengiAPIError.check_and_raise(result)

        root = etree.fromstring(result.content)
        items: List[etree.Element] = root.findall(".//getCategoryListReturn/item")

        return [xmlmap_to_model(item, ExpenseCategory, strict=self.strict) for item in items]

    def get_income_sources(
        self,
        *,
        id_list: List[int] | None = None,
    ) -> List[IncomeSource]:
        """
        Implements getSourceList API

        Original wsdl description:
            Retrievs income source list (array of arrays): [id] => Internal source ID; [parent_id] => For tree structure; [budget_family_id] => User family ID (for multiuser mode); [type] => Type of object, 2 - income source; [name] => Source name given by user; [is_hidden] => is income hidden in user interface; [sort] => User sort of source tree; If parameter [idList] is given, it will be treat as ID list of objects to retrieve# this is used for synchronization;
        """

        logger.debug(f"Getting income sources with the following params: {id_list=}")

        if id_list is not None:
            id_list_xml = generate_xml_array(id_list)
        else:
            id_list_xml = zeep.xsd.SkipValue  # type: ignore

        client = self.client

        with client.settings(raw_response=True, strict=False):
            result = client.service.getSourceList(
                self.api_key,
                self.login,
                self.password,
                idList=id_list_xml,
            )

            DrebedengiAPIError.check_and_raise(result)

        root = etree.fromstring(result.content)
        items: List[etree.Element] = root.findall(".//getSourceListReturn/item")

        return [xmlmap_to_model(item, IncomeSource, strict=self.strict) for item in items]

    def get_tags(
        self,
        *,
        id_list: List[int] | None = None,
    ) -> List[Tag]:
        """
        Implements getTagList API

        Original wsdl description:
            Retrievs tag list (array of arrays): [id] => Internal tag ID; [family_id] => User family ID (for multiuser mode); [name] => Tag name given by user; [is_hidden] => is tag hidden in user interface; [is_family] => is tag visible for all family user, or user only; [sort] => User sort of tag list; [parent_id] => For tree view; If parameter [idList] is given, it will be treat as ID list of objects to retrieve# this is used for synchronization;
        """

        logger.debug(f"Getting tags with the following params: {id_list=}")

        if id_list is not None:
            id_list_xml = generate_xml_array(id_list)
        else:
            id_list_xml = zeep.xsd.SkipValue  # type: ignore

        client = self.client

        with client.settings(raw_response=True, strict=False):
            result = client.service.getTagList(
                self.api_key,
                self.login,
                self.password,
                idList=id_list_xml,
            )

            DrebedengiAPIError.check_and_raise(result)

        root = etree.fromstring(result.content)
        items: List[etree.Element] = root.findall(".//getTagListReturn/item")

        return [xmlmap_to_model(item, Tag, strict=self.strict) for item in items]

    def get_currencies(
        self,
        *,
        id_list: List[int] | None = None,
    ) -> List[Currency]:
        """
        Implements getCurrencyList API

        Original wsdl description:
            Retrievs currency list (array of arrays) with codes and courses: [id] => Internal currency ID; [name] => Currency name, given by user; [course] => current course from sbrf(dot)ru; [code] => International currency code (for course autoupdating); [family_id] => User family ID (for multiuser mode); [is_default] => is default currency# There should be only one default currency; [is_autoupdate] => autoupdate course once per day, from sbrf(dot)ru; [is_hidden] => is currency hidden in user interface; If parameter [idList] is given, it will be treat as ID list of objects to retrieve# this is used for synchronization;
        """

        logger.debug(f"Getting currencies with the following params: {id_list=}")

        if id_list is not None:
            id_list_xml = generate_xml_array(id_list)
        else:
            id_list_xml = zeep.xsd.SkipValue  # type: ignore

        client = self.client

        with client.settings(raw_response=True, strict=False):
            result = client.service.getCurrencyList(
                self.api_key,
                self.login,
                self.password,
                idList=id_list_xml,
            )

            DrebedengiAPIError.check_and_raise(result)

        root = etree.fromstring(result.content)
        items: List[etree.Element] = root.findall(".//getCurrencyListReturn/item")

        return [xmlmap_to_model(item, Currency, strict=self.strict) for item in items]

    def get_accounts(
        self,
        *,
        id_list: List[int] | None = None,
    ) -> List[Account]:
        """
        Implements getPlaceList API

        Original wsdl description:
            Retrievs place list (array of arrays): [id] => Internal place ID; [budget_family_id] => User family ID (for multiuser mode); [type] => Type of object, 4 - places; [name] => Place name given by user; [is_hidden] => is place hidden in user interface; [is_autohide] => debts will auto hide on null balance; [is_for_duty] => Internal place for duty logic, Auto created while user adds "Waste or income duty"; [sort] => User sort of place list; [purse_of_nuid] => Not empty if place is purse of user# The value is internal user ID; [icon_id] => Place icon ID from http://www(dot)drebedengi(dot)ru/img/pl[icon_id](dot)gif; If parameter [idList] is given, it will be treat as ID list of objects to retrieve# this is used for synchronization; There is may be empty response, if user access level is limited;
        """

        logger.debug(f"Getting accounts with the following params: {id_list=}")

        if id_list is not None:
            id_list_xml = generate_xml_array(id_list)
        else:
            id_list_xml = zeep.xsd.SkipValue  # type: ignore

        client = self.client

        with client.settings(raw_response=True, strict=False):
            result = client.service.getPlaceList(
                self.api_key,
                self.login,
                self.password,
                idList=id_list_xml,
            )

            DrebedengiAPIError.check_and_raise(result)

        root = etree.fromstring(result.content)
        items: List[etree.Element] = root.findall(".//getPlaceListReturn/item")

        return [xmlmap_to_model(item, Account, strict=self.strict) for item in items]

    def get_current_revision(self) -> int:
        """
        Implements getCurrentRevision API

        Original wsdl description:
            Get current server revision number.
        """

        logger.debug("Getting current server revision")

        client = self.client

        with client.settings(raw_response=True, strict=False):
            result = client.service.getCurrentRevision(
                self.api_key,
                self.login,
                self.password,
            )

            DrebedengiAPIError.check_and_raise(result)

        root = etree.fromstring(result.content)

        return int(root.findtext(".//getCurrentRevisionReturn"))
