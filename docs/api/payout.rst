Payout API
==========

Payouts authenticate differently from the rest of the API: instead of the
``X-MerchantId``/``X-Secret`` header pair, every request is signed with
HMAC-SHA256 under a secret issued separately in the dashboard. That secret is
shown once and Platega cannot recover it.

The functionality is disabled by default on a Platega account and enabled on
request.

.. code-block:: python

   from aioplatega import PayoutClient

   async with PayoutClient(merchant_id="...", secret="...") as payouts:
       cards = await payouts.get_cards()
       result = await payouts.create_card_payout(
           card_id=cards[0].card_id,
           amount_rub=1500,
       )
       print(result.status, result.amount_usdt_debited)

.. note::
   Pass your own ``idempotency_key`` when a retry has to be safe. Without one
   a fresh key is generated per call, so a retried request would be treated as
   a second payout.

PayoutClient
------------

.. automodule:: aioplatega.payout.client
   :members:
   :show-inheritance:

Signing
-------

.. automodule:: aioplatega.payout.signing
   :members:
   :show-inheritance:
