"""Internal types for cbor2pure. Public types are imported from cbor2."""

from __future__ import annotations


class IndefiniteArray(list):
    """A list decoded from an indefinite-length CBOR array.

    Subclass of list, so isinstance(x, list) is True. The encoder
    checks for this type and emits indefinite-length encoding (0x9F
    ... 0xFF) instead of definite-length (0x8N ...).
    """

    __slots__ = ()


class IndefiniteMap(dict):
    """A dict decoded from an indefinite-length CBOR map.

    Subclass of dict, so isinstance(x, dict) is True. The encoder
    checks for this type and emits indefinite-length encoding (0xBF
    ... 0xFF) instead of definite-length (0xAN ...).
    """

    __slots__ = ()


class IndefiniteByteString(bytes):
    """Bytes decoded from an indefinite-length CBOR byte string.

    Subclass of bytes, so isinstance(x, bytes) is True. The encoder
    checks for this type and emits indefinite-length encoding with
    the original chunk boundaries preserved.
    """

    def __new__(cls, data: bytes, chunks: list[bytes] | None = None) -> IndefiniteByteString:
        instance = super().__new__(cls, data)
        instance.chunks = chunks or [data]
        return instance


class IndefiniteTextString(str):
    """A string decoded from an indefinite-length CBOR text string.

    Subclass of str, so isinstance(x, str) is True. The encoder
    checks for this type and emits indefinite-length encoding with
    the original chunk boundaries preserved.
    """

    def __new__(cls, data: str, chunks: list[str] | None = None) -> IndefiniteTextString:
        instance = super().__new__(cls, data)
        instance.chunks = chunks or [data]
        return instance


class BreakMarkerType:
    """Internal sentinel for indefinite-length decoding."""

    __slots__ = ()

    _instance = None

    def __new__(cls: type[BreakMarkerType]) -> BreakMarkerType:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "break_marker"

    def __bool__(self) -> bool:
        return True


#: Internal sentinel value for indefinite-length decoding
break_marker = BreakMarkerType()
