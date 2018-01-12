from unittest.mock import Mock, call
import pytest

from failfast.store import InProcessStore, DjangoCacheStore

NOW = 1515751348.2297542  # Current time.time()


@pytest.fixture(name="cache")
def cache_mock() -> Mock:
    mock = Mock()
    mock.get = Mock()
    mock.set = Mock()
    return mock


def test_inprocess_store() -> None:
    store = InProcessStore()

    store.set_broken("some_backend", 10)

    assert store.is_broken("some_backend")


def test_inprocess_expired() -> None:
    clock_mock = Mock(side_effect=[NOW, NOW + 10])
    store = InProcessStore(clock=clock_mock)

    store.set_broken("some_backend", 5)

    assert not store.is_broken("some_backend")


def test_inprocess_not_expired() -> None:
    clock_mock = Mock(side_effect=[NOW, NOW + 10])
    store = InProcessStore(clock=clock_mock)

    store.set_broken("some_backend", 15)

    assert store.is_broken("some_backend")


def test_inprocess_reset() -> None:
    store = InProcessStore()

    store.set_broken("some_backend", 10)
    store.reset("some_backend")

    assert not store.is_broken("some_backend")


def test_django_store_broken(cache: Mock) -> None:
    cache.get.return_value = True
    store = DjangoCacheStore(cache)

    store.set_broken("some_backend", 10)

    assert store.is_broken("some_backend")
    assert cache.set.mock_calls == [call("some_backend", True, 10)]


def test_django_store_not_broken(cache: Mock) -> None:
    cache.get.return_value = False
    store = DjangoCacheStore(cache)

    store.set_broken("some_backend", 10)

    assert not store.is_broken("some_backend")
    assert cache.set.mock_calls == [call("some_backend", True, 10)]


def test_django_reset(cache: Mock) -> None:
    cache.get.return_value = None
    store = DjangoCacheStore(cache)

    store.set_broken("some_backend", 10)
    store.reset("some_backend")

    assert not store.is_broken("some_backend")
    assert cache.delete.mock_calls == [call("some_backend")]
