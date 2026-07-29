:layout: landing

aioplatega
==========

Async Python SDK for the `Platega <https://platega.io>`_ payment API.

.. container:: buttons

   `Getting Started <getting-started.html>`_
   `API Reference <api/index.html>`_
   `GitHub <https://github.com/DOFER998/aioplatega>`_

.. grid:: 2 2 4 4
   :gutter: 3

   .. grid-item-card:: Fully async
      :class-card: sd-border-0

      Built on top of ``aiohttp`` with lazy connection pool.

   .. grid-item-card:: Type-safe
      :class-card: sd-border-0

      Pydantic v2 models with full type annotations.

   .. grid-item-card:: Command pattern
      :class-card: sd-border-0

      Reusable method objects for every API endpoint.

   .. grid-item-card:: Error handling
      :class-card: sd-border-0

      Typed exception hierarchy for every HTTP status.

Installation
------------

.. tab-set::

   .. tab-item:: pip

      .. code-block:: bash

         pip install aioplatega

   .. tab-item:: uv

      .. code-block:: bash

         uv add aioplatega

   .. tab-item:: poetry

      .. code-block:: bash

         poetry add aioplatega

Quick example
-------------

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


Releases
--------

Versions are cut by `release-please
<https://github.com/googleapis/release-please>`_, which keeps a Release PR
open against ``main`` collecting the conventional-commit messages since the
last tag. Merging it bumps the version, writes ``CHANGELOG.md``, tags, and
publishes to PyPI. Pushing code publishes nothing.

Specification sources
---------------------

Platega publishes its API in more than one place, and they do not fully agree.
This library is built against all of them:

- **OpenAPI**, one document per endpoint, linked from
  `docs.platega.io/llms.txt <https://docs.platega.io/llms.txt>`_. Append
  ``.md`` to any documentation URL to get the machine-readable spec for that
  page. This is the authority for paths, fields and schemas.
- The rendered pages at `docs.platega.io <https://docs.platega.io/>`_, whose
  prose carries operational rules the schemas omit — the ``metadata.userId``
  requirement, callback URL restrictions, and the payout signing scheme.
- An older `GitBook <https://platega-io.gitbook.io/platega.io-api-dokumentaciya>`_
  that still documents the exchange-rate endpoint and payment method ``10``,
  neither of which appears in the current reference.

Where the sources disagree, this library accepts the union and types the
affected fields permissively, so a value one specification omits does not make
a response unreadable.

.. toctree::
   :hidden:

   getting-started
   api/index
