"""PG-HMAC signing for the Payout API.

The vendor publishes a worked Python example; these lock our implementation to
the same canonical string and the same body bytes, since a mismatch on either
side is rejected as an authentication failure rather than a clear error.
"""

import base64
import hashlib
import hmac

from aioplatega.payout.signing import (
    EMPTY_BODY_SHA256,
    authorization_header,
    build_string_to_sign,
    serialize_body,
    sign,
)

SECRET = "test-secret"
MERCHANT = "29ef0000-0000-0000-0000-000000000000"


class TestBodySerialization:
    def test_no_whitespace_between_tokens(self):
        """The signed bytes go on the wire verbatim; stray spaces break the signature."""
        body = serialize_body({"a": 1, "b": "x"})
        assert body == b'{"a":1,"b":"x"}'

    def test_none_body_is_empty(self):
        assert serialize_body(None) == b""

    def test_empty_body_hash_matches_the_documented_constant(self):
        assert EMPTY_BODY_SHA256 == (
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        )

    def test_key_order_is_preserved(self):
        """Reordering keys would change the hash, so insertion order must survive."""
        assert serialize_body({"b": 1, "a": 2}) == b'{"b":1,"a":2}'


class TestStringToSign:
    def test_five_newline_separated_elements(self):
        sts = build_string_to_sign("POST", "/api/v1/payouts/card-rub", 1719403200, "idem", b"{}")
        parts = sts.split("\n")
        assert parts[0] == "POST"
        assert parts[1] == "/api/v1/payouts/card-rub"
        assert parts[2] == "1719403200"
        assert parts[3] == "idem"
        assert parts[4] == hashlib.sha256(b"{}").hexdigest()

    def test_get_leaves_an_empty_idempotency_line(self):
        """The docs keep the field's line in the string even when it is unused."""
        sts = build_string_to_sign("GET", "/api/v1/cards", 1719403200, "", b"")
        assert sts.split("\n")[3] == ""
        assert sts.split("\n")[4] == EMPTY_BODY_SHA256

    def test_method_is_upper_cased(self):
        assert build_string_to_sign("get", "/p", 1, "", b"").startswith("GET\n")


class TestSignature:
    def test_matches_a_hand_computed_hmac(self):
        sts = build_string_to_sign("GET", "/api/v1/cards", 1719403200, "", b"")
        expected = base64.b64encode(
            hmac.new(SECRET.encode(), sts.encode(), hashlib.sha256).digest()
        ).decode()
        assert sign(SECRET, sts) == expected

    def test_signature_is_base64(self):
        sts = build_string_to_sign("GET", "/api/v1/cards", 1719403200, "", b"")
        base64.b64decode(sign(SECRET, sts), validate=True)

    def test_different_secret_changes_the_signature(self):
        sts = build_string_to_sign("GET", "/api/v1/cards", 1719403200, "", b"")
        assert sign(SECRET, sts) != sign("other", sts)

    def test_different_timestamp_changes_the_signature(self):
        a = sign(SECRET, build_string_to_sign("GET", "/p", 1, "", b""))
        b = sign(SECRET, build_string_to_sign("GET", "/p", 2, "", b""))
        assert a != b


class TestAuthorizationHeader:
    def test_layout(self):
        header = authorization_header(MERCHANT, 1719403200, "abc123==")
        assert header == f"PG-HMAC kid={MERCHANT}, ts=1719403200, sig=abc123=="
