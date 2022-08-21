#!/usr/bin/env python
"""Tests for `drebedengi` package."""

import os
from pathlib import Path

from drebedengi import DrebedengiAPI
from drebedengi.model import ChangeRecord, Transaction, TransactionType

import pytest
from attrs import evolve

from typing import Callable, List, Tuple


@pytest.fixture(scope="module")
def credentials() -> Tuple[str, str, str]:
    api_key = "demo_api"
    login = "demo@example.com"
    password = "demo"

    dotenv_path = Path(os.getcwd()) / ".env"
    if dotenv_path.exists():
        for line in dotenv_path.read_text().splitlines():
            key, value = line.split("=")
            match key:
                case "DREBEDENGI_API_KEY":
                    api_key = value
                case "DREBEDENGI_LOGIN":
                    login = value
                case "DREBEDENGI_PASSWORD":
                    password = value

    return api_key, login, password


@pytest.fixture(scope="module")
def test_api(credentials: Tuple[str, str, str]) -> DrebedengiAPI:
    """Test API."""
    api_key, login, password = credentials

    return DrebedengiAPI(
        api_key=api_key,
        login=login,
        password=password,
    )


@pytest.fixture(scope="module")
def sample_transaction(test_api: DrebedengiAPI) -> Callable[..., Transaction]:
    """Gets a single sample transaction."""

    def get_sample_transaction(type: TransactionType = TransactionType.ANY) -> Transaction:
        return test_api.get_transactions(include_types=type)[0]

    return get_sample_transaction


@pytest.fixture(scope="module")
def current_revision(test_api: DrebedengiAPI) -> int:
    """Returns current demo account revision."""
    return test_api.get_current_revision()


def test_get_current_revision(test_api: DrebedengiAPI) -> None:
    """Test get_current_revision"""
    assert test_api.get_current_revision() > 0


def test_get_transactions_defaults(test_api: DrebedengiAPI) -> None:
    """Test get transactions."""
    transactions = test_api.get_transactions()

    # for transfer transactions, there are two records in the list
    assert (
        sum([1 if tr.operation_type != TransactionType.TRANSFER else 0.5 for tr in transactions])
        == 20
    )


def test_get_transaction_by_id(
    test_api: DrebedengiAPI, sample_transaction: Callable[..., Transaction]
) -> None:
    """Test get transaction by id."""
    sample_tr = sample_transaction()
    transactions = test_api.get_transactions(id_list=[sample_tr.id])
    assert len(transactions) == 1

    # For some reason drebedengi returns transactions without UTC timestamps when id_list is passed.
    comp_trans = evolve(sample_tr, oper_utc_timestamp=None)
    assert transactions[0] == comp_trans


def test_get_changes(
    test_api: DrebedengiAPI, current_revision: int, credentials: Tuple[str, str, str]
) -> None:
    """Test get_changes"""
    api_key, login, password = credentials
    if api_key == "demo_api":
        # Skip test if demo account, it doesn't provide changes
        return

    changes: List[ChangeRecord] = []
    ref_revision = current_revision - 1
    while not changes:
        changes = test_api.get_changes(revision=ref_revision)
        if not changes:
            # fail if no changes found after 10 attempts
            assert current_revision - ref_revision < 100000
            current_revision -= 10000


def test_get_expense_categories(test_api: DrebedengiAPI) -> None:
    """Test get categories."""
    categories = test_api.get_expense_categories()

    assert len(categories) > 0


def test_get_expense_categories_by_id(
    test_api: DrebedengiAPI, sample_transaction: Callable[..., Transaction]
) -> None:
    """Test get category by id."""
    categories = test_api.get_expense_categories(
        id_list=[sample_transaction(TransactionType.EXPENSE).budget_object_id]
    )
    assert len(categories) == 1


def test_get_income_sources(test_api: DrebedengiAPI) -> None:
    """Test get income sources."""
    sources = test_api.get_income_sources()

    assert len(sources) > 0


def test_get_income_sources_by_id(
    test_api: DrebedengiAPI, sample_transaction: Callable[..., Transaction]
) -> None:
    """Test get income source by id."""
    sources = test_api.get_income_sources(
        id_list=[sample_transaction(TransactionType.INCOME).budget_object_id]
    )
    assert len(sources) == 1


def test_get_tags(test_api: DrebedengiAPI) -> None:
    """Test get tags."""
    tags = test_api.get_tags()

    assert len(tags) > 0

    tag = test_api.get_tags(id_list=[tags[0].id])[0]

    assert tag.id == tags[0].id


def test_get_currencies(test_api: DrebedengiAPI) -> None:
    """Test get currencies."""
    currencies = test_api.get_currencies()

    assert len(currencies) > 0


def test_get_currencies_by_id(
    test_api: DrebedengiAPI, sample_transaction: Callable[..., Transaction]
) -> None:
    """Test get currency by id."""
    currency = test_api.get_currencies(id_list=[sample_transaction().currency_id])
    assert len(currency) == 1


def test_get_accounts(test_api: DrebedengiAPI) -> None:
    """Test get accounts."""
    accounts = test_api.get_accounts()

    assert len(accounts) > 0


def test_get_accounts_by_id(
    test_api: DrebedengiAPI, sample_transaction: Callable[..., Transaction]
) -> None:
    """Test get account by id."""
    account = test_api.get_accounts(id_list=[sample_transaction().account_id])
    assert len(account) == 1
