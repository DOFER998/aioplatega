Exceptions
==========

.. code-block:: text

   PlategaError
   ├── PlategaAPIError
   │   ├── PlategaBadRequestError   (400)
   │   ├── PlategaUnauthorizedError (401)
   │   ├── PlategaForbiddenError    (403)
   │   ├── PlategaNotFoundError     (404)
   │   └── PlategaServerError       (5xx)
   ├── PlategaNetworkError
   └── ClientDecodeError

.. automodule:: aioplatega.exceptions.base
   :members:
   :undoc-members:
   :show-inheritance:
