"""Response shapes captured from the live API.

The published specification is empty or wrong for some of these endpoints —
the conversions example in the docs is literally ``{}`` — so these payloads
were recorded from real calls and are the reference the models are built to.
"""

import pytest

from aioplatega.types import ConversionsResponse, RateResponse
from tests.factories import MERCHANT_ID, OPERATION_ID, TRANSACTION_ID, fake

TRACE_ID = fake.hexify("^" * 18)

CONVERSIONS = {
    "operations": [
        {
            "id": OPERATION_ID,
            "merchantId": MERCHANT_ID,
            "exchangeRate": 83.895,
            "operationDate": "2026-07-29T14:25:00.988453Z",
            "sourceAmount": 5300.0,
            "targetAmount": 63.17420585,
            "sourceCurrency": "RUB",
            "targetCurrency": "USDT",
            "transactionsStartDate": "2026-07-28T02:16:41.700457Z",
            "transactionsEndDate": "2026-07-28T21:19:10.456154Z",
            "processedTransactionsCount": 11,
            "description": "Автоматическая конвертация RUB в USDT",
            "createdAt": "2026-07-29T14:25:00.988448Z",
        }
    ],
    "pagination": {"page": 0, "size": 1, "total": 96},
}

RATE = {
    "id": TRANSACTION_ID,
    "rate": 87.68,
    "currencyFrom": "USDT",
    "currencyTo": "RUB",
    "paymentMethod": 2,
    "merchantId": MERCHANT_ID,
}


class TestConversions:
    """The API answers with `operations` and `pagination`, not `content`."""

    def test_operations_are_parsed(self):
        parsed = ConversionsResponse.model_validate(CONVERSIONS)
        assert len(parsed.operations) == 1

    def test_operation_fields(self):
        op = ConversionsResponse.model_validate(CONVERSIONS).operations[0]
        assert op.id == OPERATION_ID
        assert op.exchange_rate == 83.895
        assert op.source_amount == 5300.0
        assert op.target_amount == 63.17420585
        assert op.source_currency == "RUB"
        assert op.target_currency == "USDT"
        assert op.processed_transactions_count == 11

    def test_pagination_is_parsed(self):
        page = ConversionsResponse.model_validate(CONVERSIONS).pagination
        assert page is not None
        assert page.page == 0
        assert page.size == 1
        assert page.total == 96

    def test_empty_response_is_tolerated(self):
        parsed = ConversionsResponse.model_validate({"operations": [], "pagination": None})
        assert parsed.operations == []

    def test_response_is_iterable_over_operations(self):
        parsed = ConversionsResponse.model_validate(CONVERSIONS)
        assert [o.source_currency for o in parsed] == ["RUB"]
        assert len(parsed) == 1


class TestRate:
    def test_live_fields_are_parsed(self):
        parsed = RateResponse.model_validate(RATE)
        assert parsed.rate == 87.68
        assert parsed.payment_method == 2
        assert parsed.id == TRANSACTION_ID
        assert parsed.merchant_id == MERCHANT_ID

    def test_updated_at_is_optional(self):
        """Documented in the GitBook example but absent from live answers."""
        assert RateResponse.model_validate(RATE).updated_at is None


class TestErrorEnvelope:
    """Errors carry more than a message; traceId is what support asks for."""

    @pytest.mark.parametrize(
        ("body", "code", "trace"),
        [
            (
                {
                    "code": "Common:VAL_0001",
                    "type": 4001,
                    "message": "Wrong input parameters",
                    "data": [{"key": "paymentMethod", "message": "Subscription"}],
                    "traceId": TRACE_ID,
                },
                "Common:VAL_0001",
                TRACE_ID,
            ),
            ({"message": "plain"}, None, None),
        ],
    )
    def test_envelope_fields_are_surfaced(self, body, code, trace):
        from aioplatega.exceptions import PlategaAPIError
        from aioplatega.session.errors import raise_for_status

        with pytest.raises(PlategaAPIError) as exc_info:
            raise_for_status(400, body, "/x")

        assert exc_info.value.code == code
        assert exc_info.value.trace_id == trace

    def test_field_errors_are_surfaced(self):
        from aioplatega.exceptions import PlategaAPIError
        from aioplatega.session.errors import raise_for_status

        body = {
            "message": "Wrong input parameters",
            "data": [{"key": "paymentMethod", "message": "Subscription"}],
        }
        with pytest.raises(PlategaAPIError) as exc_info:
            raise_for_status(400, body, "/x")

        assert exc_info.value.errors == [{"key": "paymentMethod", "message": "Subscription"}]

    def test_repr_mentions_the_trace_id(self):
        from aioplatega.exceptions import PlategaAPIError

        exc = PlategaAPIError("boom", method="/x", status_code=400, trace_id="t-1")
        assert "t-1" in repr(exc)

    def test_repr_omits_absent_envelope_fields(self):
        from aioplatega.exceptions import PlategaAPIError

        bare = repr(PlategaAPIError("boom", method="/x", status_code=400))
        assert bare == "PlategaAPIError(message='boom', method='/x', status_code=400)"

    def test_repr_includes_code_and_field_errors(self):
        from aioplatega.exceptions import PlategaAPIError

        exc = PlategaAPIError(
            "boom",
            method="/x",
            status_code=400,
            code="Common:VAL_0001",
            errors=[{"key": "paymentMethod", "message": "Subscription"}],
        )
        text = repr(exc)
        assert "Common:VAL_0001" in text
        assert "paymentMethod" in text
