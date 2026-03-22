from typing import Any

# Import types from cbor2 for compatibility
from cbor2 import CBORDecodeEOF as CBORDecodeEOF
from cbor2 import CBORDecodeError as CBORDecodeError
from cbor2 import CBORDecodeValueError as CBORDecodeValueError
from cbor2 import CBOREncodeError as CBOREncodeError
from cbor2 import CBOREncodeTypeError as CBOREncodeTypeError
from cbor2 import CBOREncodeValueError as CBOREncodeValueError
from cbor2 import CBORError as CBORError
from cbor2 import CBORSimpleValue as CBORSimpleValue
from cbor2 import CBORTag as CBORTag
from cbor2 import FrozenDict as FrozenDict
from cbor2 import undefined as undefined

# Import pure Python encoder/decoder implementations
from ._decoder import CBORDecoder as CBORDecoder
from ._decoder import load as load
from ._decoder import loads as loads
from ._encoder import CBOREncoder as CBOREncoder
from ._encoder import dump as dump
from ._encoder import dumps as dumps
from ._encoder import shareable_encoder as shareable_encoder

# Indefinite-length container types for round-trip fidelity
from ._types import IndefiniteArray as IndefiniteArray
from ._types import IndefiniteByteString as IndefiniteByteString
from ._types import IndefiniteMap as IndefiniteMap
from ._types import IndefiniteTextString as IndefiniteTextString

# Re-export imports so they look like they live directly in this package
key: str
value: Any
for key, value in list(locals().items()):
    if callable(value) and getattr(value, "__module__", "").startswith("cbor2pure."):
        value.__module__ = __name__
