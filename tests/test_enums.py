from aioplatega.enums import PaymentMethodInt, PaymentStatus


class TestPaymentMethodInt:
    def test_values(self):
        assert PaymentMethodInt.SBP_QR == 2
        assert PaymentMethodInt.CARDS_RUB == 10
        assert PaymentMethodInt.CARD_ACQUIRING == 11
        assert PaymentMethodInt.INTERNATIONAL_ACQUIRING == 12
        assert PaymentMethodInt.CRYPTO == 13

    def test_is_int(self):
        assert isinstance(PaymentMethodInt.SBP_QR, int)

    def test_member_count(self):
        assert len(PaymentMethodInt) == 5

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
