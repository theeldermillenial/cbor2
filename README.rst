.. image:: https://github.com/cffls/cbor2pure/actions/workflows/test.yml/badge.svg
  :target: https://github.com/cffls/cbor2pure/actions/workflows/test.yml
  :alt: Testing Status
.. image:: https://github.com/cffls/cbor2pure/actions/workflows/publish.yml/badge.svg
  :target: https://github.com/cffls/cbor2pure/actions/workflows/publish.yml
  :alt: Publish Status
.. image:: https://img.shields.io/pypi/v/cbor2pure
  :target: https://pypi.org/project/cbor2pure/
  :alt: PyPI

About
=====

cbor2pure is the CBOR (`RFC 8949`_) decoder from cbor2_, with decode hooks that report how each
item was framed in the input:

* whether an array used definite or indefinite-length encoding;
* the chunk lengths of an indefinite-length byte or text string;
* whether a map used indefinite-length encoding.

A decoded value does not carry this framing, so it cannot be re-encoded to the same bytes. Some
formats need exactly that. On Cardano, for example, transaction ids, script data hashes and
signatures cover the original bytes of transactions and Plutus datums, and those bytes mix
definite and indefinite framing freely. With these hooks a caller can record the framing while
decoding, rather than parsing the input a second time.

cbor2pure is **decode-only, on cbor2's own types**:

* ``CBORDecoder``, ``load``, ``loads`` and ``shareable_decoder`` are cbor2pure's own. The first
  three take the hook parameters.
* Everything else is cbor2's own object, re-exported: ``dumps``, ``dump``, ``CBOREncoder``,
  ``shareable_encoder``, ``CBORTag``, ``CBORSimpleValue``, ``frozendict``, ``undefined`` and all
  exception classes.
* The decoder returns cbor2's classes and raises cbor2's exceptions. A decoded tag is a
  ``cbor2.CBORTag``, ``except cbor2.CBORDecodeError`` catches cbor2pure's decode errors, and
  ``cbor2.dumps(cbor2pure.loads(data))`` behaves as it does with cbor2's own decoder.

This keeps one encoder and one set of value classes in the process, so cbor2pure can be swapped
in for cbor2's decoder without changing any ``isinstance`` check or ``except`` clause.

.. _RFC 8949: https://www.rfc-editor.org/rfc/rfc8949.html
.. _cbor2: https://github.com/agronholm/cbor2

Decode hooks
------------

Each hook is a keyword argument of ``CBORDecoder``, ``load`` and ``loads``, and is called only
when it is set. Its return value replaces the decoded item.

``array_hook(value, indefinite)`` is called for every array, with the decoded ``list`` (a
``tuple`` when decoded as immutable) and whether it used indefinite-length encoding::

    import cbor2pure

    class IndefiniteList(list):
        pass

    def array_hook(value, indefinite):
        return IndefiniteList(value) if indefinite else value

    value = cbor2pure.loads(bytes.fromhex("9f0102ff"), array_hook=array_hook)
    assert type(value) is IndefiniteList

``indefinite_string_hook(value, chunk_lengths)`` is called for indefinite-length byte and text
strings only, with the joined ``bytes`` or ``str`` and a tuple of each chunk's length in bytes::

    chunks = []
    value = cbor2pure.loads(
        bytes.fromhex("5f4201024103ff"),
        indefinite_string_hook=lambda value, lengths: chunks.append(lengths) or value,
    )
    assert value == b"\x01\x02\x03" and chunks == [(2, 1)]

``indefinite_map_hook(value)`` is called for indefinite-length maps only, with the decoded
``dict`` (a ``frozendict`` when decoded as immutable). It runs before ``object_hook``::

    class IndefiniteDict(dict):
        pass

    value = cbor2pure.loads(bytes.fromhex("bf0102ff"), indefinite_map_hook=IndefiniteDict)
    assert type(value) is IndefiniteDict

The `customizing guide`_ covers how the hooks interact with tags, shared values, string
references and map keys.

.. _customizing guide: https://github.com/cffls/cbor2pure/blob/master/docs/customizing.rst

Differences from cbor2
----------------------

* The content of a tag with no registered decoder is decoded according to the ``immutable``
  flag (cbor2 6.1.5 always decodes it as immutable).
* Because cbor2's ``CBORTag.value`` is read-only, a tag with no registered decoder is created
  after its content. A value-sharing reference (tag 29) to such a tag from inside its own value
  therefore raises ``CBORDecodeError`` instead of building the cycle. Only data that uses value
  sharing (tags 28 and 29) can contain this.

Name history
------------

cbor2pure 5.x was a copy of cbor2's pure-Python implementation, for users who needed it rather
than cbor2's C extension. cbor2 6 replaced both implementations with a single Rust extension and
no longer has a pure-Python one, so from 6.x cbor2pure is compiled as well. The name stays for
continuity on PyPI. The 5.x releases remain available there (``pip install "cbor2pure<6"``,
together with ``"cbor2<6"``) for anyone who needs pure Python.

Credits
-------

cbor2 is written and maintained by `Alex Grönholm`_ and its contributors. Nearly all of the code
in this repository is theirs, taken from cbor2 unchanged. Please report problems that are not
specific to the decode hooks to cbor2_.

.. _Alex Grönholm: https://github.com/agronholm

Installation
============

::

    pip install cbor2pure

This also installs cbor2, whose classes the decoder uses. Wheels are built for the same platforms
and Python versions as cbor2's.

To build from source you need Python >= 3.10 (or PyPy3 3.11+) and a `Rust toolchain`_.

.. _Rust toolchain: https://rust-lang.org/tools/install/

Versioning
==========

cbor2pure ``X.Y.Z`` is built on cbor2 ``X.Y.Z``, and ``X.Y.Z.postN`` is a cbor2pure-only
revision of it. Each release requires a cbor2 of the same major version.

Usage
=====

cbor2pure is used like cbor2; see cbor2's `documentation <https://cbor2.readthedocs.io/>`_. The
command line tool is ``cbor2pure`` (or ``python -m cbor2pure.tool``) and works like cbor2's.

License
=======

MIT, the same as cbor2. See ``LICENSE.txt``.
