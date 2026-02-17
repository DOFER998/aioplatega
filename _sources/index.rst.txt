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

      aiogram-style method objects for every API endpoint.

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


.. toctree::
   :hidden:

   getting-started
   api/index
