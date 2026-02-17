##########
aioplatega
##########

.. image:: https://img.shields.io/pypi/l/aioplatega.svg?style=flat-square
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

.. image:: https://img.shields.io/pypi/v/aioplatega.svg?style=flat-square
    :target: https://pypi.python.org/pypi/aioplatega
    :alt: PyPi Package Version

.. image:: https://img.shields.io/pypi/dm/aioplatega.svg?style=flat-square
    :target: https://pypi.python.org/pypi/aioplatega
    :alt: Downloads

.. image:: https://img.shields.io/pypi/pyversions/aioplatega.svg?style=flat-square
    :target: https://pypi.python.org/pypi/aioplatega
    :alt: Supported Python Versions

.. image:: https://img.shields.io/github/actions/workflow/status/DOFER998/aioplatega/tests.yml?branch=main&style=flat-square
    :target: https://github.com/DOFER998/aioplatega/actions
    :alt: Tests

**aioplatega** is a modern and fully asynchronous SDK for the
`Platega payment API <https://platega.io>`_ written in Python 3.10+ using
`asyncio <https://docs.python.org/3/library/asyncio.html>`_ and
`aiohttp <https://github.com/aio-libs/aiohttp>`_.

Documentation: `aioplatega docs <https://DOFER998.github.io/aioplatega/>`_


Features
========

- Fully asynchronous (`asyncio <https://docs.python.org/3/library/asyncio.html>`_)
- Type-safe with `Pydantic v2 <https://docs.pydantic.dev/latest/>`_ models and full type annotations
- Supports `mypy <http://mypy-lang.org/>`_ strict mode
- aiogram-style command pattern for API methods
- Typed exception hierarchy for every HTTP status
- Lazy connection pool with ``aiohttp``


Installation
============

.. code-block:: bash

    pip install aioplatega

.. code-block:: bash

    uv add aioplatega


Quick Start
===========

.. code-block:: python

    import asyncio
    from aioplatega import Platega, PaymentMethodInt, PaymentDetails

    async def main():
        async with Platega(merchant_id="your-id", secret="your-secret") as client:
            result = await client.create_transaction(
                payment_method=PaymentMethodInt.SBP_QR,
                payment_details=PaymentDetails(amount=100.0, currency="RUB"),
            )
            print(result.transaction_id, result.status)

    asyncio.run(main())


Community
=========

.. image:: https://img.shields.io/badge/Telegram-Chat-blue.svg?style=flat-square&logo=telegram
    :target: https://t.me/platega_sdk
    :alt: Telegram Chat

- 🇷🇺 `@platega_sdk <https://t.me/platega_sdk>`_
