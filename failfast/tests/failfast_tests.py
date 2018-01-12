from unittest.mock import Mock, call

import pytest

from failfast import failfast, FailfastException
from failfast.store import Store


@pytest.fixture(name="store")
def store_mock():
    return Mock(spec=Store)


def test_original_function_works(store):
    store.is_broken.return_value = False

    @failfast("test", timeout_seconds=1, store=store, exceptions=[ZeroDivisionError])
    def f(a, b, kwvalue=2):
        return (a + b) * kwvalue

    assert f(3, 5, kwvalue=7) == 56


def test_expected_error_with_no_previous_error(store):
    store.is_broken.return_value = False

    @failfast("test", timeout_seconds=1, store=store, exceptions=[ZeroDivisionError])
    def f():
        return 1 / 0

    with pytest.raises(ZeroDivisionError):
        f()

    assert store.is_broken.mock_calls == [call("test")]
    assert store.set_broken.mock_calls == [call("test", 1)]


def test_expected_error_with_previous_error(store):
    store.is_broken.return_value = True

    @failfast("test", timeout_seconds=1, store=store, exceptions=[ZeroDivisionError])
    def f():
        return 1 / 0

    with pytest.raises(FailfastException):
        f()
    assert store.is_broken.mock_calls == [call("test")]
    assert store.set_broken.mock_calls == []


def test_unexpected_error_with_no_previous_error(store):
    store.is_broken.return_value = False

    @failfast("test", timeout_seconds=1, store=store, exceptions=[ValueError])
    def f():
        return 1 / 0

    with pytest.raises(ZeroDivisionError):
        f()
    assert store.is_broken.mock_calls == [call("test")]
    assert store.set_broken.mock_calls == []


def test_unexpected_error_with_previous_error(store):
    store.is_broken.return_value = True

    @failfast("test", timeout_seconds=1, store=store, exceptions=[ValueError])
    def f():
        return 1 / 0

    with pytest.raises(FailfastException):
        f()
    assert store.is_broken.mock_calls == [call("test")]
    assert store.set_broken.mock_calls == []
