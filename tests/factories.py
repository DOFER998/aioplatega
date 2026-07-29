"""Deterministic fake data, generated with faker.

Values are produced at import time because several tests need them inside
``parametrize`` decorators, which run before fixtures exist. The seed is fixed
so a failing run reproduces from the test name alone.

Payloads captured from the live API keep their real shape but never their real
identifiers — those are regenerated here.
"""

from faker import Faker

SEED = 20260729

fake = Faker()
Faker.seed(SEED)

TRANSACTION_ID = str(fake.uuid4())
SUBSCRIPTION_ID = str(fake.uuid4())
MERCHANT_ID = str(fake.uuid4())
CARD_ID = str(fake.uuid4())
RECORD_ID = str(fake.uuid4())
OPERATION_ID = str(fake.uuid4())

SECRET = fake.password(length=32, special_chars=False)
PAYOUT_SECRET = fake.password(length=32, special_chars=False)

CARD_NUMBER = fake.credit_card_number(card_type="mastercard")
CARD_LAST4 = CARD_NUMBER[-4:]
CARD_HOLDER = fake.name()
CUSTOMER_EMAIL = fake.email()
ORDER_ID = str(fake.random_int(min=1000, max=9999))
DESCRIPTION = fake.sentence(nb_words=3)


def uuid() -> str:
    """A fresh identifier, for tests that need one that collides with nothing."""
    return str(fake.uuid4())
