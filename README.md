Failfast [![CircleCI](https://circleci.com/gh/ticketea/failfast.svg?style=svg)](https://circleci.com/gh/ticketea/failfast) [![PyPI version](https://img.shields.io/pypi/v/failfast.svg)]() [![Python Versions](https://img.shields.io/pypi/pyversions/failfast.svg)]()
=======

Pythonic Circuit Breaker implementation.

Some features:

   * Works in a distributed environment (multiple processes or hosts).
   * Framework independent, easy integration with Django/Flask, etc.
   * Django integration included.
   * Development environment friendly (can be disabled by a setting).
   * Python 3 only (yes, a feature).


Failfast is a simple decorator intended to protect your application from slow backends.

Suppose you have a traditional thread/process pool based web application, and that on users
HTTP requests your application needs to synchronously retrieve some information from a third
party service. Now suppose this third party service for some reason starts to take too long
to respond to your requests, then your application will run out of threads/processes and die.

The solution to this problem, is to set a timeout, but doing just that only alleviates the problem,
as your application will still have to wait for that timeout to elapse on every request. Setting
this timeout too low might make it fail earlier. How would you solve this?

Enter failfast, a pythonic Circuit Breaker implemented as a decorator which, when an exception
is seen, it will return immediately for any subsequent calls during a specified period of time, thus
leaving any external service time to recover, and keeping your application as snappy as possible.


Installation
-----------

Install the latest stable version from Pypi with `pip install failfast`.


Usage
-----

```python
import requests
from requests.exceptions import Timeout
from failfast import failfast

@failfast("sales_api", 60, exceptions=[Timeout])
def get_invoices():

    # Will raise a Timeout exception if it takes more than 3 seconds
    response = requests.get("http://api.example.com/invoices/", timeout=3)

    return response.content

```

In the previous snipped, we wrapped `get_invoices` so that, when a `Timeout` happens, for the next
60 seconds, calling `get_invoices` will throw a `FailfastException` immediately.


You would use it as follows:

```python
from failfast import FailfastException

def my_view(request):
    try:
        return get_invoices()
    except FailfastException:
        logger.info("API is broken at this moment")
        return "Some cached value or a message to retry later to the user"

```

Failfast options
----------------

Failfast configuration is provided as arguments to the decorator.

  * **name**: A key that uniquely identifies the backend API call.
  * **timeout**: Time (in seconds) to automatically throw a `FailfastException` after first failure.
  * **store**: A store to persist currently broken services.
  * **exceptions:** A list of exceptions that are handled by Failfast. Defaults to any `Exception`.
  * **enabled:** If set to `False`, failfast will just call the underlying function as if it were not installed.
    * You might want to set this to `True` in your development environment.

Distributed usage
-----------------

If your application consists of many processes and/or many hosts, then the information
of a given backend service being down and/or available should be somehow shared.

For this purpose, you can pass a custom `store` argument to failfast, see [store.py](failfast/store.py) for examples.


Django support
--------------

If you are using Django, setup the cache framework to use a shared store like redis, memcache, database, etc
and then use the decorator like:
```python
from failfast import failfast
from failfast.store import  DjangoCacheStore
from django.core.cache import cache

@failfast("name", 60, DjangoCacheStore(cache))
def my_fn():
    ...
```

Development environment
=======================

Run `make shell` and then use the tests/examples.


Running tests
=============

To run all tests in all environments and python versions supported, run:

```bash
make test
```

To run a single test in a single environment, from within a `make shell` run:

```bash
tox -e py36 -- failfast/tests/store_tests.py::test_inprocess_reset
```
