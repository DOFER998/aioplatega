from aioplatega.exceptions import (
    ClientDecodeError,
    PlategaAPIError,
    PlategaBadRequestError,
    PlategaError,
    PlategaForbiddenError,
    PlategaNetworkError,
    PlategaNotFoundError,
    PlategaServerError,
    PlategaUnauthorizedError,
)


class TestExceptionHierarchy:
    def test_base_inherits_exception(self):
        assert issubclass(PlategaError, Exception)

    def test_api_error_inherits_base(self):
        assert issubclass(PlategaAPIError, PlategaError)

    def test_http_errors_inherit_api_error(self):
        assert issubclass(PlategaBadRequestError, PlategaAPIError)
        assert issubclass(PlategaUnauthorizedError, PlategaAPIError)
        assert issubclass(PlategaForbiddenError, PlategaAPIError)
        assert issubclass(PlategaNotFoundError, PlategaAPIError)
        assert issubclass(PlategaServerError, PlategaAPIError)

    def test_network_error_inherits_base(self):
        assert issubclass(PlategaNetworkError, PlategaError)

    def test_decode_error_inherits_base(self):
        assert issubclass(ClientDecodeError, PlategaError)


class TestPlategaAPIError:
    def test_attributes(self):
        exc = PlategaAPIError(
            message="Bad request",
            method="/transaction/process",
            status_code=400,
            body={"error": "invalid"},
        )
        assert exc.message == "Bad request"
        assert exc.method == "/transaction/process"
        assert exc.status_code == 400
        assert exc.body == {"error": "invalid"}

    def test_str(self):
        exc = PlategaAPIError(message="Something went wrong")
        assert str(exc) == "Something went wrong"

    def test_repr(self):
        exc = PlategaAPIError(
            message="Not found",
            method="/test",
            status_code=404,
        )
        result = repr(exc)
        assert "PlategaAPIError" in result
        assert "Not found" in result
        assert "404" in result

    def test_defaults(self):
        exc = PlategaAPIError(message="error")
        assert exc.method is None
        assert exc.status_code is None
        assert exc.body is None


class TestPlategaBadRequestError:
    def test_repr(self):
        exc = PlategaBadRequestError(
            message="Invalid payload",
            method="/test",
            status_code=400,
        )
        assert "PlategaBadRequestError" in repr(exc)


class TestPlategaNetworkError:
    def test_construction(self):
        exc = PlategaNetworkError("Connection refused")
        assert str(exc) == "Connection refused"


class TestClientDecodeError:
    def test_construction(self):
        exc = ClientDecodeError("Failed to parse JSON")
        assert str(exc) == "Failed to parse JSON"
