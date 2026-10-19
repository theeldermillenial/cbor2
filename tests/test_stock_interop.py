"""Decoded values are cbor2's own objects, and errors are cbor2's own exceptions."""

import sys

import cbor2
import pytest

import cbor2pure


@pytest.mark.parametrize(
    "name",
    [
        "CBORTag",
        "CBORSimpleValue",
        "undefined",
        "CBORError",
        "CBORDecodeError",
        "CBORDecodeEOF",
        "CBOREncodeError",
        "CBOREncoder",
        "dumps",
        "dump",
        "shareable_encoder",
    ],
)
def test_reexported_from_cbor2(name: str) -> None:
    assert getattr(cbor2pure, name) is getattr(cbor2, name)


def test_decoder_is_own() -> None:
    assert cbor2pure.CBORDecoder.__module__ == "cbor2pure"
    assert cbor2.CBORDecoder.__module__ == "cbor2"
    assert cbor2pure.loads is not cbor2.loads


@pytest.mark.parametrize(
    "payload",
    [
        "d8799f0102ff",  # indefinite array in an unknown-number tag
        "d87a80",  # tag 122, empty array
        "c11a514b67b0",  # tag 1, decoded by a built-in decoder
        "f7",  # undefined
        "f3",  # simple value 19
        "f8ff",  # simple value 255
        "a1a1010203",  # map key decoded as an immutable map
        "d9010283010203",  # tag 258 set
        "d9010446010203040506",  # tag 260 with 6 bytes: MAC address
    ],
)
def test_round_trip_through_cbor2(payload: str) -> None:
    data = bytes.fromhex(payload)
    ours = cbor2pure.loads(data)
    stock = cbor2.loads(data)
    # Equality is not compared: the content of an unknown-number tag decodes as mutable
    # here (a list) and as immutable in cbor2 (a tuple). Both encode to the same bytes.
    assert type(ours) is type(stock)
    assert cbor2.dumps(ours) == cbor2.dumps(stock)


def test_tag_and_value_types() -> None:
    tag = cbor2pure.loads(bytes.fromhex("d8799f0102ff"))
    assert isinstance(tag, cbor2.CBORTag)
    assert cbor2pure.loads(b"\xf7") is cbor2.undefined
    assert isinstance(cbor2pure.loads(b"\xf3"), cbor2.CBORSimpleValue)
    if sys.hexversion < 51314855:
        key = next(iter(cbor2pure.loads(bytes.fromhex("a1a1010203"))))
        assert type(key) is cbor2.frozendict


@pytest.mark.parametrize(
    "payload, exc",
    [
        (b"\x82\x01", cbor2.CBORDecodeEOF),
        (b"\xff", cbor2.CBORDecodeError),
        (b"\x1c", cbor2.CBORDecodeError),
    ],
)
def test_errors_are_cbor2_exceptions(payload: bytes, exc: type[Exception]) -> None:
    with pytest.raises(exc) as info:
        cbor2pure.loads(payload)
    assert type(info.value).__module__ == "cbor2"
