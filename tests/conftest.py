import struct

import pytest

import cbor2pure
import cbor2pure._decoder
import cbor2pure._encoder
import cbor2pure._types


@pytest.fixture
def will_overflow():
    """
    Construct an array/string/bytes length which would cause a memory error
    on decode. This should be less than sys.maxsize (the max integer index)
    """
    bit_size = struct.calcsize("P") * 8
    huge_length = 1 << (bit_size - 8)
    return struct.pack("Q", huge_length)


class Module:
    # Mock module class
    pass


@pytest.fixture(scope="session")
def impl():
    # Pure Python implementation only
    module = Module()
    for source in (cbor2pure, cbor2pure._types, cbor2pure._encoder, cbor2pure._decoder):
        for name in dir(source):
            setattr(module, name, getattr(source, name))
    return module
