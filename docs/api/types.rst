Types
=====

All Pydantic models are **immutable** (``frozen=True``) and support extra fields.

Base
----

.. automodule:: aioplatega.types.base
   :members:
   :show-inheritance:

PaymentDetails
--------------

.. automodule:: aioplatega.types.payment_details
   :members:
   :show-inheritance:

CreateTransactionRequest
------------------------

.. automodule:: aioplatega.types.create_transaction_request
   :members:
   :show-inheritance:

CreateTransactionResponse
-------------------------

.. automodule:: aioplatega.types.create_transaction_response
   :members:
   :show-inheritance:

TransactionStatusResponse
-------------------------

.. automodule:: aioplatega.types.transaction_status_response
   :members:
   :show-inheritance:

RateResponse
------------

.. automodule:: aioplatega.types.rate_response
   :members:
   :show-inheritance:

ConversionItem
--------------

.. automodule:: aioplatega.types.conversion_item
   :members:
   :show-inheritance:

ConversionsResponse
-------------------

.. automodule:: aioplatega.types.conversions_response
   :members:
   :show-inheritance:

CallbackPayload
---------------

.. automodule:: aioplatega.types.callback_payload
   :members:
   :show-inheritance:

PaymentLinkResponse
-------------------

.. automodule:: aioplatega.types.payment_link_response
   :members:
   :show-inheritance:

H2HQrResponse
-------------

.. automodule:: aioplatega.types.h2h_qr_response
   :members:
   :show-inheritance:

Balances
--------

.. autoclass:: aioplatega.types.balance_item.BalanceItem
   :members:
   :show-inheritance:

``GET /balance/all`` returns a bare array. ``BalancesResponse`` is
``RootModel[list[BalanceItem]]`` — iterate it directly.

Transaction exports
-------------------

.. automodule:: aioplatega.types.transaction_export_request
   :members:
   :show-inheritance:

Transaction export rows
-----------------------

.. autoclass:: aioplatega.types.transaction_export_item.TransactionExportItem
   :members:
   :show-inheritance:

The JSON export returns a bare array. ``TransactionExportResponse`` is
``RootModel[list[TransactionExportItem]]`` — iterate it directly.

ExportUrlResponse
-----------------

.. automodule:: aioplatega.types.export_url_response
   :members:
   :show-inheritance:

Cancellation
------------

.. automodule:: aioplatega.types.cancel_supported_response
   :members:
   :show-inheritance:

CancelTransactionResponse
-------------------------

.. automodule:: aioplatega.types.cancel_transaction_response
   :members:
   :show-inheritance:

Subscription
------------

.. automodule:: aioplatega.types.subscription
   :members:
   :show-inheritance:

SubscriptionPaymentDetails
--------------------------

.. automodule:: aioplatega.types.subscription_payment_details
   :members:
   :show-inheritance:

SubscriptionListResponse
------------------------

.. automodule:: aioplatega.types.subscription_list_response
   :members:
   :show-inheritance:

CreateSubscriptionResponse
--------------------------

.. automodule:: aioplatega.types.create_subscription_response
   :members:
   :show-inheritance:

CancelSubscriptionResponse
--------------------------

.. automodule:: aioplatega.types.cancel_subscription_response
   :members:
   :show-inheritance:

Subscription callbacks
----------------------

.. automodule:: aioplatega.types.subscription_callbacks
   :members:
   :show-inheritance:

Saved cards
-----------

.. autoclass:: aioplatega.types.saved_card.SavedCard
   :members:
   :show-inheritance:

``GET /api/v1/cards`` returns a bare array. ``SavedCardsResponse`` is
``RootModel[list[SavedCard]]`` — iterate it directly.

Payouts
-------

.. automodule:: aioplatega.types.payout
   :members:
   :show-inheritance:
