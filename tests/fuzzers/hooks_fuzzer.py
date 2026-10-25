"""Fuzz the framing hooks (array_hook, indefinite_string_hook, indefinite_map_hook).

Every hook, tag_hook and object_hook is set. Decoding must either succeed or raise
CBORError; any other exception is a failure. For input that decodes, the hook calls are
checked against an independent framing parser: array_hook fires once per array with the
right indefinite flag, indefinite_string_hook once per indefinite string with the exact
chunk lengths, indefinite_map_hook once per indefinite map, in decode order, and every
value a hook returns appears in the result unless a built-in tag decoder consumed it.
"""

import sys

import atheris

from cbor2pure import CBORError, CBORTag, loads

# Tags with a built-in decoder: their content is consumed, not kept in the result.
_SMALL_TAGS = (0, 1, 2, 3, 4, 5, 25, 28, 29, 30, 35, 36, 37, 52, 54, 100, 256, 258, 260, 261)
BUILTIN_TAGS = frozenset((*_SMALL_TAGS, 1004, 43000, 55799))
_WRAPPERS: dict[type, type | None] = {}


def wrap(value):
    cls = type(value)
    if cls not in _WRAPPERS:
        try:
            _WRAPPERS[cls] = type("Wrapped" + cls.__name__, (cls,), {})
        except TypeError:
            _WRAPPERS[cls] = None
    wrapper = _WRAPPERS[cls]
    return value if wrapper is None else wrapper(value)


def read_head(data, offset):
    initial = data[offset]
    major, info = initial >> 5, initial & 31
    offset += 1
    if info < 24:
        return major, info, offset
    if info < 28:
        size = 1 << (info - 24)
        if offset + size > len(data):
            raise ValueError("truncated head")
        return major, int.from_bytes(data[offset : offset + size], "big"), offset + size
    if info == 31:
        return major, None, offset
    raise ValueError("reserved additional information")


def expected_hook_calls(data):
    """The hook calls the first item of ``data`` should produce, in firing order, as
    (call, consumed) pairs; consumed is True inside a tag with a built-in decoder."""
    calls = []
    stack = []  # [major, expected item count or None, items seen, chunks, consumed, tag]
    offset = 0
    while True:
        major, arg, offset = read_head(data, offset)
        consumed = bool(stack) and (
            stack[-1][4] or (stack[-1][0] == 6 and stack[-1][5] in BUILTIN_TAGS)
        )
        is_break = major == 7 and arg is None
        if stack and stack[-1][0] in (2, 3):
            top = stack[-1]
            if is_break:
                stack.pop()
                calls.append((("string", top[0], tuple(top[3])), top[4]))
            elif major == top[0] and arg is not None and offset + arg <= len(data):
                top[3].append(arg)
                offset += arg
                continue
            else:
                raise ValueError("invalid chunk")
        elif is_break:
            if not stack or stack[-1][1] is not None or stack[-1][0] not in (4, 5):
                raise ValueError("unexpected break")
            top = stack.pop()
            if top[0] == 5 and top[2] % 2:
                raise ValueError("break after a map key")
            call = ("array", True, top[2]) if top[0] == 4 else ("map", top[2] // 2)
            calls.append((call, top[4]))
        elif arg is None:
            if major not in (2, 3, 4, 5):
                raise ValueError("indefinite length on a scalar")
            stack.append([major, None, 0, [], consumed, None])
            continue
        elif major in (2, 3):
            if offset + arg > len(data):
                raise ValueError("truncated string")
            offset += arg
        elif major in (4, 5, 6) and (arg or major == 6):
            count = 1 if major == 6 else arg * (2 if major == 5 else 1)
            stack.append([major, count, 0, [], consumed, arg])
            continue
        elif major == 4:
            calls.append((("array", False, 0), consumed))
        # An item is complete: count it in its parent, closing finished parents.
        while stack:
            parent = stack[-1]
            parent[2] += 1
            if parent[1] is None or parent[2] < parent[1]:
                break
            stack.pop()
            if parent[0] == 4:
                calls.append((("array", False, parent[2]), parent[4]))
        else:
            return calls


def reachable(value):
    seen, stack = set(), [value]
    while stack:
        item = stack.pop()
        if id(item) in seen:
            continue
        seen.add(id(item))
        if isinstance(item, dict) or hasattr(item, "keys"):
            for key, member in item.items():
                stack += [key, member]
        elif isinstance(item, (list, tuple, set, frozenset)):
            stack.extend(item)
        elif type(item) is CBORTag:
            stack.append(item.value)
    return seen


def test_one_input(data: bytes) -> None:
    fdp = atheris.FuzzedDataProvider(data)
    flags = fdp.ConsumeIntInRange(0, 7)
    payload = fdp.ConsumeBytes(fdp.remaining_bytes())
    allow_duplicate_keys = bool(flags & 4)
    calls: list = []

    def array_hook(value, indefinite):
        calls.append((("array", indefinite, len(value)), wrap(value)))
        return calls[-1][1]

    def indefinite_string_hook(value, chunk_lengths):
        major = 2 if isinstance(value, bytes) else 3
        calls.append((("string", major, chunk_lengths), wrap(value)))
        return calls[-1][1]

    def indefinite_map_hook(value):
        calls.append((("map", len(value)), wrap(value)))
        return calls[-1][1]

    try:
        value = loads(
            payload,
            immutable=bool(flags & 1),
            str_errors="replace" if flags & 2 else "strict",
            allow_duplicate_keys=allow_duplicate_keys,
            array_hook=array_hook,
            indefinite_string_hook=indefinite_string_hook,
            indefinite_map_hook=indefinite_map_hook,
            tag_hook=lambda tag, immutable: tag,
            object_hook=lambda mapping, immutable: mapping,
        )
    except CBORError:
        return

    try:
        expected = expected_hook_calls(payload)
    except (IndexError, ValueError) as exc:
        raise AssertionError(f"decoded ill-formed input ({exc})") from None
    actual = [call for call, _ in calls]
    assert len(actual) == len(expected), (actual, expected)
    if allow_duplicate_keys:
        # Duplicate keys collapse, so a decoded map may have fewer entries than pairs.
        for index, (got, (want, _)) in enumerate(zip(actual, expected)):
            if got[0] == want[0] == "map" and got[1] <= want[1]:
                actual[index] = want
    assert actual == [want for want, _ in expected], (actual, expected)
    if not allow_duplicate_keys:
        found = reachable(value)
        for (call, hooked), (_, consumed) in zip(calls, expected):
            assert consumed or id(hooked) in found, f"{call} result missing from the output"


if __name__ == "__main__":
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()
