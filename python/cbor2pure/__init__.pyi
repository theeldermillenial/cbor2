import sys
from collections.abc import Callable, Mapping, Sequence
from typing import IO, Any, TypeAlias, final, overload

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

if sys.hexversion < 51314855:
    from cbor2 import frozendict as frozendict

if sys.version_info >= (3, 13):
    pass
else:
    pass

if sys.version_info >= (3, 12):
    from collections.abc import Buffer
else:
    from typing_extensions import Buffer

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

TagHook: TypeAlias = Callable[[CBORTag, bool], Any]
SemanticDecoderCallback: TypeAlias = Callable[[Any, bool], Any]
ObjectHook: TypeAlias = Callable[[Mapping[Any, Any], bool], Any]
ArrayHook: TypeAlias = Callable[[Sequence[Any], bool], Any]
IndefiniteStringHook: TypeAlias = Callable[[bytes | str, tuple[int, ...]], Any]
IndefiniteMapHook: TypeAlias = Callable[[Mapping[Any, Any]], Any]
EncoderHook: TypeAlias = Callable[[CBOREncoder, Any], Any]
ShareableDecoderCallback: TypeAlias = Callable[[Any], Any]
ShareableDecoderInitializer: TypeAlias = Callable[[bool], tuple[Any, ShareableDecoderCallback]]

@final
class CBORDecoder:
    fp: IO[bytes]
    tag_hook: TagHook | None
    object_hook: ObjectHook | None
    array_hook: ArrayHook | None
    indefinite_string_hook: IndefiniteStringHook | None
    indefinite_map_hook: IndefiniteMapHook | None
    str_errors: str
    def __new__(
        cls,
        fp: IO[bytes],
        *,
        tag_hook: TagHook | None = ...,
        object_hook: ObjectHook | None = ...,
        array_hook: ArrayHook | None = ...,
        indefinite_string_hook: IndefiniteStringHook | None = ...,
        indefinite_map_hook: IndefiniteMapHook | None = ...,
        semantic_decoders: Mapping[int, SemanticDecoderCallback | ShareableDecoderInitializer]
        | None = ...,
        str_errors: str = ...,
        read_size: int = ...,
        max_depth: int = ...,
        allow_indefinite: bool = ...,
        allow_duplicate_keys: bool = ...,
    ) -> Self: ...

    # Properties
    @property
    def read_size(self) -> int: ...
    @property
    def max_depth(self) -> int: ...
    @property
    def allow_indefinite(self) -> bool: ...
    @property
    def allow_duplicate_keys(self) -> bool: ...
    def decode(self, *, immutable: bool = ...) -> Any: ...
    def read(self, amount: int, /) -> bytes: ...

def load(
    fp: IO[bytes],
    *,
    tag_hook: TagHook | None = ...,
    object_hook: ObjectHook | None = ...,
    array_hook: ArrayHook | None = ...,
    indefinite_string_hook: IndefiniteStringHook | None = ...,
    indefinite_map_hook: IndefiniteMapHook | None = ...,
    semantic_decoders: Mapping[int, SemanticDecoderCallback | ShareableDecoderInitializer]
    | None = ...,
    str_errors: str = ...,
    read_size: int = ...,
    max_depth: int = ...,
    allow_indefinite: bool = ...,
    allow_duplicate_keys: bool = ...,
    immutable: bool = ...,
) -> Any: ...
def loads(
    data: Buffer,
    *,
    tag_hook: TagHook | None = ...,
    object_hook: ObjectHook | None = ...,
    array_hook: ArrayHook | None = ...,
    indefinite_string_hook: IndefiniteStringHook | None = ...,
    indefinite_map_hook: IndefiniteMapHook | None = ...,
    semantic_decoders: Mapping[int, SemanticDecoderCallback | ShareableDecoderInitializer]
    | None = ...,
    str_errors: str = ...,
    max_depth: int = ...,
    allow_indefinite: bool = ...,
    allow_duplicate_keys: bool = ...,
    immutable: bool = ...,
) -> Any: ...
@overload
def shareable_decoder(func: ShareableDecoderInitializer, /) -> ShareableDecoderInitializer: ...
@overload
def shareable_decoder(
    *, name: str | None = ..., immutable: bool = ...
) -> Callable[[ShareableDecoderInitializer], ShareableDecoderCallback]: ...
