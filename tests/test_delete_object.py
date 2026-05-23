"""Unit tests for api.delete_object (mocked HTTP)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from drebedengi import DrebedengiAPI


SUCCESS_RESPONSE = (
    b'<?xml version="1.0" encoding="UTF-8"?>'
    b'<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"'
    b' xmlns:ns1="urn:ddengi" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
    b' xmlns:xsd="http://www.w3.org/2001/XMLSchema">'
    b"<SOAP-ENV:Body><ns1:deleteObjectResponse>"
    b'<deleteObjectReturn xsi:type="xsd:int">1</deleteObjectReturn>'
    b"</ns1:deleteObjectResponse></SOAP-ENV:Body></SOAP-ENV:Envelope>"
)


def _mk_api(content: bytes = SUCCESS_RESPONSE) -> DrebedengiAPI:
    a = DrebedengiAPI.__new__(DrebedengiAPI)
    a.api_key, a.login, a.password = "k", "l", "p"
    a.soap_url, a.strict = "fake", True
    fake_client = MagicMock()
    fake_response = MagicMock()
    fake_response.ok = True
    fake_response.status_code = 200
    fake_response.content = content
    fake_client.service.deleteObject.return_value = fake_response
    fake_client.settings.return_value.__enter__ = lambda self: None
    fake_client.settings.return_value.__exit__ = lambda *args: None
    a.client = fake_client
    return a


def test_delete_object_returns_true_on_success() -> None:
    api = _mk_api()
    assert api.delete_object(object_id=12345, object_type="waste") is True
    call_kwargs = api.client.service.deleteObject.call_args.kwargs
    assert call_kwargs["id"] == 12345
    assert call_kwargs["type"] == "waste"


def test_delete_object_passes_credentials_positionally() -> None:
    api = _mk_api()
    api.delete_object(object_id=1, object_type="tag")
    args = api.client.service.deleteObject.call_args.args
    assert args == ("k", "l", "p")
