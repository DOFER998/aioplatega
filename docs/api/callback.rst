Callbacks
=========

Platega authenticates a callback by echoing your own ``X-MerchantId`` and
``X-Secret`` headers back at you; there is no signature over the body. The
comparison is done with :func:`hmac.compare_digest`, so a wrong secret cannot
be recovered by timing the response.

.. automodule:: aioplatega.callback
   :members:
   :show-inheritance:
