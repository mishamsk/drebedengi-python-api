#!/usr/bin/env python
"""Tests for `drebedengi` package."""

import os
from pathlib import Path

from drebedengi import DrebedengiAPI
from drebedengi.model import ChangeRecord, Transaction, TransactionType

import pytest
from attrs import evolve

from typing import List, Tuple


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
def sample_transaction(test_api: DrebedengiAPI) -> Transaction:
    """Gets a single sample transaction."""
    return test_api.get_transactions()[0]


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


def test_get_transaction_by_id(test_api: DrebedengiAPI, sample_transaction: Transaction) -> None:
    """Test get transaction by id."""
    transactions = test_api.get_transactions(id_list=[sample_transaction.id])
    assert len(transactions) == 1

    # For some reason drebedengi returns transactions without UTC timestamps when id_list is passed.
    comp_trans = evolve(sample_transaction, oper_utc_timestamp=None)
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
