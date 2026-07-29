Exceptions
==========

.. code-block:: text

   PlategaError
   ├── PlategaAPIError
   │   ├── PlategaBadRequestError          (400)
   │   ├── PlategaUnauthorizedError        (401)
   │   ├── PlategaForbiddenError           (403)
   │   ├── PlategaNotFoundError            (404)
   │   ├── PlategaConflictError            (409)
   │   ├── PlategaUnprocessableEntityError (422)
   │   ├── PlategaRateLimitError           (429)
   │   └── PlategaServerError              (5xx)
   ├── PlategaNetworkError
   ├── PlategaValidationError
   └── ClientDecodeError

Every failure raised by this library derives from ``PlategaError``, so a single
``except PlategaError`` is enough to catch all of them.

``PlategaValidationError`` is raised before a request leaves the process, when
the arguments cannot form a valid request. Any other 4xx status that has no
dedicated class arrives as the generic ``PlategaAPIError``.

.. automodule:: aioplatega.exceptions.base
   :members:
   :undoc-members:
   :show-inheritance:
