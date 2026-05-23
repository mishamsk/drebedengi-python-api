"""Unit tests for xmlmap_to_model and models that hit XML edge cases."""

from __future__ import annotations

from lxml import etree

from drebedengi.model import Currency
from drebedengi.utils import xmlmap_to_model


NS = 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"'


def _make_currency_xml(*, with_code: str | None) -> etree.Element:
    code_tag = (
        f'<value xsi:type="xsd:string">{with_code}</value>'
        if with_code is not None
        else '<value xsi:type="xsd:string"/>'
    )
    src = f"""<item {NS}>
        <item><key>id</key><value xsi:type="xsd:string">42</value></item>
        <item><key>name</key><value xsi:type="xsd:string">руб</value></item>
        <item><key>course</key><value xsi:type="xsd:string">1</value></item>
        <item><key>code</key>{code_tag}</item>
        <item><key>family_id</key><value xsi:type="xsd:string">283054</value></item>
        <item><key>is_default</key><value xsi:type="xsd:string">t</value></item>
        <item><key>is_autoupdate</key><value xsi:type="xsd:string">f</value></item>
        <item><key>is_hidden</key><value xsi:type="xsd:string">f</value></item>
    </item>"""
    return etree.fromstring(src)


def test_currency_with_iso_code():
    xml = _make_currency_xml(with_code="USD")
    cur = xmlmap_to_model(xml, Currency, strict=True)
    assert cur.id == 42
    assert cur.user_name == "руб"
    assert cur.currency_code == "USD"
    assert cur.is_default is True


def test_currency_without_iso_code_does_not_crash():
    """Regression: user-defined currencies (e.g. RUB nicknamed 'руб') may have an empty <code>.
    The model must tolerate this and set currency_code=None instead of raising ValueError.
    """
    xml = _make_currency_xml(with_code=None)
    cur = xmlmap_to_model(xml, Currency, strict=True)
    assert cur.id == 42
    assert cur.user_name == "руб"
    assert cur.currency_code is None
