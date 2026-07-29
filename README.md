<div align="center">

# aioplatega

**Modern, fully asynchronous SDK for the [Platega](https://platega.io) payment API.**

[![PyPI](https://img.shields.io/pypi/v/aioplatega.svg?style=flat-square)](https://pypi.python.org/pypi/aioplatega)
[![Python](https://img.shields.io/pypi/pyversions/aioplatega.svg?style=flat-square)](https://pypi.python.org/pypi/aioplatega)
[![Downloads](https://img.shields.io/pypi/dm/aioplatega.svg?style=flat-square)](https://pypi.python.org/pypi/aioplatega)
[![Tests](https://img.shields.io/github/actions/workflow/status/DOFER998/aioplatega/tests.yml?branch=main&style=flat-square)](https://github.com/DOFER998/aioplatega/actions)
[![License](https://img.shields.io/pypi/l/aioplatega.svg?style=flat-square)](https://opensource.org/licenses/MIT)

[Documentation](https://DOFER998.github.io/aioplatega/) · [Getting started](https://DOFER998.github.io/aioplatega/getting-started.html) · [API reference](https://DOFER998.github.io/aioplatega/api/index.html)

</div>

## Install

```bash
pip install aioplatega
```

```bash
uv add aioplatega
```

Requires Python 3.12 or newer.

## Quick start

```python
import asyncio

from aioplatega import PaymentDetails, PaymentMethodInt, Platega


async def main():
    async with Platega(merchant_id="your-id", secret="your-secret") as client:
        result = await client.create_transaction(
            payment_method=PaymentMethodInt.SBP_QR,
            payment_details=PaymentDetails(amount=100.0, currency="RUB"),
            description="Order #42",
        )
        print(result.redirect)


asyncio.run(main())
```

Send the payer to `result.redirect`, then wait for the callback.

```python
from aioplatega import PaymentStatus
from aioplatega.exceptions import PlategaValidationError


@app.route("/callback", methods=["POST"])  # Flask
def callback():
    try:
        payload = client.verify_callback(request.headers, request.get_data())
    except PlategaValidationError:
        return "", 401

    if payload.status == PaymentStatus.CONFIRMED:
        mark_paid(payload.payload)
    return "", 200
```

> [!IMPORTANT]
> Platega authenticates callbacks by echoing your own `X-MerchantId` and `X-Secret` back at you. There is no signature over the body, so the comparison is all that stands between you and a forged callback. `verify_callback` does it with `hmac.compare_digest`; if you roll your own, do the same.

## What it covers

| | |
|---|---|
| **Payments** | Hosted links with or without a fixed method, H2H QR codes, status lookup |
| **Subscriptions** | Recurring SBP charges, with callbacks for each charge and status change |
| **Refunds** | Cancellation, and a check of whether it is possible and what it costs |
| **Reporting** | Balances, conversions, CSV / Excel / JSON exports |
| **Payouts** | RUB card payouts over the separate PG-HMAC signed API |

Every endpoint is reachable two ways: a method on the client, or a method object dispatched through it.

```python
from aioplatega.methods import CreateTransaction

result = await client(CreateTransaction(...))
```

See the [API reference](https://DOFER998.github.io/aioplatega/api/index.html) for the full surface.

## Design

- **Fully asynchronous**, built on [`aiohttp`](https://github.com/aio-libs/aiohttp) with a lazily created connection pool
- **Type safe.** [Pydantic v2](https://docs.pydantic.dev/latest/) models throughout, complete annotations, `mypy --strict` clean
- **Immutable.** Every model is frozen, and tolerant of unknown fields so a new attribute added server side does not break you
- **One exception hierarchy.** Everything raised derives from `PlategaError`, including argument errors caught before a request goes out

```
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
```

<details>
<summary><b>A note on the API specification</b></summary>

Platega publishes its API in three places and they do not fully agree: the OpenAPI documents linked from [`docs.platega.io/llms.txt`](https://docs.platega.io/llms.txt), the prose on the rendered pages, and an older GitBook that still documents endpoints and payment methods the current reference omits.

This library is built against all three. Where they conflict it accepts the union and types the affected fields permissively, so a value one specification leaves out does not make a whole response unreadable. The cases where that matters are called out in the relevant docstrings.

</details>

## Payouts

Payouts are a separate client, because they are a separate security model: a secret issued once that Platega cannot recover, an HMAC-SHA256 signature over every request, and an idempotency key on every write.

```python
from aioplatega import PayoutClient

async with PayoutClient(merchant_id="your-id", secret="payout-secret") as payouts:
    cards = await payouts.get_cards()
    result = await payouts.create_card_payout(
        card_id=cards[0].card_id,
        amount_rub=1500,
        idempotency_key="order-42-payout",
    )
```

> [!WARNING]
> Pass your own `idempotency_key` whenever a retry has to be safe. Without one a fresh key is generated per call, so a retried request counts as a second payout.

The feature is disabled by default on a Platega account and enabled on request.

## Contributing

```bash
make install     # sync every dependency group and install the pre-commit hooks
make lint        # ruff, formatting, mypy
make test        # pytest with coverage
make docs-serve  # docs with live reload on :8000
```

Commits follow [Conventional Commits](https://www.conventionalcommits.org/); releases are cut from them by [release-please](https://github.com/googleapis/release-please).

## License

[MIT](LICENSE)
