"""cbor2's decoder with Cardano decode hooks.

Decoding (``load``, ``loads``, ``CBORDecoder``) is this package's own; it accepts every
cbor2 keyword plus ``array_hook``, ``indefinite_string_hook`` and ``indefinite_map_hook``.
Every other name is cbor2's own object, re-exported: decoded values are cbor2's classes,
errors are cbor2's exceptions, and encoding is cbor2's encoder, so values round-trip
through ``cbor2.dumps`` and pass ``isinstance`` checks against cbor2.
"""

import sys
from collections.abc import Callable, Mapping
from typing import Any, TypeAlias

from cbor2 import CBORDecodeEOF as CBORDecodeEOF
from cbor2 import CBORDecodeError as CBORDecodeError
from cbor2 import CBOREncodeError as CBOREncodeError
from cbor2 import CBOREncoder as CBOREncoder
from cbor2 import CBOREncodeTypeError as CBOREncodeTypeError
from cbor2 import CBOREncodeValueError as CBOREncodeValueError
from cbor2 import CBORError as CBORError
from cbor2 import CBORSimpleValue as CBORSimpleValue
from cbor2 import CBORTag as CBORTag
from cbor2 import dump as dump
from cbor2 import dumps as dumps
from cbor2 import shareable_encoder as shareable_encoder
from cbor2 import undefined as undefined

from ._cbor2 import CBORDecoder as CBORDecoder
from ._cbor2 import load as load
from ._cbor2 import loads as loads
from ._cbor2 import shareable_decoder as shareable_decoder

if sys.hexversion < 51314855:
    from cbor2 import frozendict as frozendict

TagHook: TypeAlias = Callable[[CBORTag, bool], Any]
SemanticDecoderCallback: TypeAlias = Callable[[Any, bool], Any]
ObjectHook: TypeAlias = Callable[[Mapping[Any, Any], bool], Any]
EncoderHook: TypeAlias = Callable[[CBOREncoder, Any], Any]
ShareableDecoderCallback: TypeAlias = Callable[[Any], Any]
ShareableDecoderInitializer: TypeAlias = Callable[[bool], tuple[Any, ShareableDecoderCallback]]

del Any, Callable, Mapping, TypeAlias, sys
