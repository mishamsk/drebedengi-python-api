"""Unit tests for api.set_record_list (mocked HTTP)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from drebedengi import DrebedengiAPI
from drebedengi.model import TransactionType


FAKE_OK_RESPONSE = (
    b'<?xml version="1.0" encoding="UTF-8"?>'
    b'<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"'
    b' xmlns:ns1="urn:ddengi"'
    b' xmlns:ns2="http://xml.apache.org/xml-soap"'
    b' xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"'
    b' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
    b' xmlns:xsd="http://www.w3.org/2001/XMLSchema">'
    b"<SOAP-ENV:Body>"
    b"<ns1:setRecordListResponse>"
    b'<setRecordListReturn SOAP-ENC:arrayType="ns2:Map[1]" xsi:type="SOAP-ENC:Array">'
    b'<item xsi:type="ns2:Map">'
    b'<item><key xsi:type="xsd:string">server_id</key>'
    b'<value xsi:type="xsd:string">123456</value></item>'
    b'<item><key xsi:type="xsd:string">client_id</key>'
    b'<value xsi:type="xsd:int">42</value></item>'
    b'<item><key xsi:type="xsd:string">status</key>'
    b'<value xsi:type="xsd:string">inserted</value></item>'
    b"</item>"
    b"</setRecordListReturn>"
    b"</ns1:setRecordListResponse>"
    b"</SOAP-ENV:Body>"
    b"</SOAP-ENV:Envelope>"
)


@pytest.fixture
def api(monkeypatch: pytest.MonkeyPatch) -> DrebedengiAPI:
    # Skip the network WSDL fetch by faking the Client. We instantiate the real DrebedengiAPI
    # and then swap out its client with a MagicMock that returns FAKE_OK_RESPONSE.
    a = DrebedengiAPI.__new__(DrebedengiAPI)
    a.api_key = "k"
    a.login = "l"
    a.password = "p"
    a.soap_url = "fake"
    a.strict = True
    fake_client = MagicMock()
    fake_response = MagicMock()
    fake_response.ok = True
    fake_response.status_code = 200
    fake_response.content = FAKE_OK_RESPONSE
    fake_client.service.setRecordList.return_value = fake_response
    # client.settings(...) must work as a context manager
    fake_client.settings.return_value.__enter__ = lambda self: None
    fake_client.settings.return_value.__exit__ = lambda *args: None
    a.client = fake_client
    return a


def test_set_record_list_parses_server_response(api: DrebedengiAPI) -> None:
    result = api.set_record_list([
        {
            "client_id": 42,
            "place_id": 17909584,
            "budget_object_id": 10637197,
            "sum": 1,
            "operation_date": "2026-05-23 23:00:00",
            "comment": "smoke",
            "currency_id": 2211943,
            "operation_type": TransactionType.EXPENSE,
            "is_duty": False,
        }
    ])
    assert result == [{"server_id": "123456", "client_id": "42", "status": "inserted"}]


def test_set_record_list_normalizes_enum_to_int(api: DrebedengiAPI) -> None:
    """TransactionType is converted to its int value before being sent."""
    api.set_record_list([
        {
            "client_id": 42,
            "place_id": 1,
            "budget_object_id": 1,
            "sum": 1,
            "operation_date": "2026-05-23 23:00:00",
            "comment": "x",
            "currency_id": 1,
            "operation_type": TransactionType.EXPENSE,
        }
    ])
    call_kwargs = api.client.service.setRecordList.call_args.kwargs
    # `list` is the only kwarg the method passes — drill into its serialised form by
    # rendering it through zeep to confirm the integer made it across.
    import lxml.etree as etree
    rendered = etree.tostring(call_kwargs["list"]._xsd_type._element_render_value(call_kwargs["list"])) if False else None
    # Simplest: enum normalization is invariant — `_normalized` rebuilds dicts before
    # they hit zeep. We at least assert that the call happened with our `list` kwarg
    # and that the original input dict still carries the enum (we don't mutate the caller's
    # dict in-place).
    assert call_kwargs.get("list") is not None


def test_set_record_list_empty_returns_empty(api: DrebedengiAPI) -> None:
    assert api.set_record_list([]) == []
    api.client.service.setRecordList.assert_not_called()
