from aioplatega.enums import PaymentMethodInt, PaymentStatus


class TestPaymentMethodInt:
    def test_values(self):
        assert PaymentMethodInt.SBP_QR == 2
        assert PaymentMethodInt.ERIP == 3
        assert PaymentMethodInt.CARDS_RUB == 10
        assert PaymentMethodInt.CARD_ACQUIRING == 11
        assert PaymentMethodInt.INTERNATIONAL_ACQUIRING == 12
        assert PaymentMethodInt.CRYPTO == 13

    def test_is_int(self):
        assert isinstance(PaymentMethodInt.SBP_QR, int)

    def test_member_count(self):
        assert len(PaymentMethodInt) == 6

    def test_documented_values(self):
        """docs.platega.io publishes [2, 3, 11, 12, 13]; 10 is ours alone."""
        assert {m.value for m in PaymentMethodInt} - {10} == {2, 3, 11, 12, 13}

    def test_from_value(self):
        assert PaymentMethodInt(2) is PaymentMethodInt.SBP_QR

    def test_invalid_value(self):
        import pytest

        with pytest.raises(ValueError):
            PaymentMethodInt(999)


class TestPaymentStatus:
    def test_values(self):
        assert PaymentStatus.PENDING == "PENDING"
        assert PaymentStatus.CANCELED == "CANCELED"
        assert PaymentStatus.CONFIRMED == "CONFIRMED"
        assert PaymentStatus.CHARGEBACKED == "CHARGEBACKED"

    def test_is_str(self):
        assert isinstance(PaymentStatus.PENDING, str)

    def test_member_count(self):
        assert len(PaymentStatus) == 4

    def test_from_value(self):
        assert PaymentStatus("CONFIRMED") is PaymentStatus.CONFIRMED


class TestSubscriptionEnums:
    def test_subscription_status_values(self):
        from aioplatega.enums import SubscriptionStatus

        assert {m.value for m in SubscriptionStatus} == {
            "PendingAgreement",
            "Active",
            "PastDue",
            "Cancelled",
            "Failed",
        }

    def test_callback_subscription_status_values(self):
        from aioplatega.enums import CallbackSubscriptionStatus

        assert {m.value for m in CallbackSubscriptionStatus} == {
            "SUBSCRIPTION_ACTIVATED",
            "SUBSCRIPTION_PAST_DUE",
            "SUBSCRIPTION_CANCELLED",
            "SUBSCRIPTION_FAILED",
        }

    def test_subscription_interval_values(self):
        from aioplatega.enums import SubscriptionInterval

        assert {m.value for m in SubscriptionInterval} == {"1", "2", "3", "4"}

    def test_str_enums_format_as_their_value(self):
        from aioplatega.enums import SubscriptionStatus

        assert f"{SubscriptionStatus.ACTIVE}" == "Active"
