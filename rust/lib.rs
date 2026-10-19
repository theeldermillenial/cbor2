#![allow(clippy::too_many_arguments)]

mod decoder;
mod types;
mod utils;

use pyo3::prelude::pymodule;

/// A Python module implemented in Rust.
#[pymodule]
mod _cbor2 {
    use pyo3::buffer::PyBuffer;
    use pyo3::exceptions::PyTypeError;
    use pyo3::prelude::*;
    use pyo3::sync::PyOnceLock;
    use pyo3::types::{PyBytes, PyMapping};

    #[pymodule_export]
    use crate::decoder::CBORDecoder;

    #[pymodule_export]
    use crate::decoder::shareable_decoder;

    // The value and error classes are stock cbor2's (re-exported by the Python package).

    pub static SYS_MAXSIZE: PyOnceLock<u64> = PyOnceLock::new();
    pub static BREAK_MARKER: PyOnceLock<Py<PyAny>> = PyOnceLock::new();

    ///  Deserialize an object from an open file.
    ///
    /// :param fp: the file to read from (any file-like object opened for reading in binary mode)
    /// :param tag_hook:
    ///     callable that takes 2 arguments: the decoder instance, and the :class:`.CBORTag`
    ///     to be decoded. This callback is invoked for any tags for which there is no
    ///     specific decoder. The return value is substituted for the :class:`.CBORTag`
    ///     object in the deserialized output
    /// :param object_hook:
    ///     callable that takes 2 arguments: the decoder instance, and a dictionary. This
    ///     callback is invoked for each deserialized :class:`dict` object. The return value
    ///     is substituted for the dict in the deserialized output.
    /// :param array_hook:
    ///     callable that takes 2 arguments: the decoded array (a :class:`list`, or a
    ///     :class:`tuple` when ``immutable`` is true), and a boolean that is :data:`True` if
    ///     the array used indefinite-length encoding. This callback is invoked for each
    ///     deserialized array, and its return value is substituted for the array in the
    ///     deserialized output. It allows callers to preserve the distinction between
    ///     definite- and indefinite-length arrays, which is otherwise lost after decoding.
    /// :param indefinite_string_hook:
    ///     callable that takes 2 arguments: the decoded string (a :class:`bytes` for a byte
    ///     string, or a :class:`str` for a text string), and a :class:`tuple` holding the
    ///     length in bytes of each chunk, in encoding order. This callback is invoked only for
    ///     strings that used indefinite-length encoding, and its return value is substituted
    ///     for the string in the deserialized output. Definite-length strings never invoke it.
    /// :param indefinite_map_hook:
    ///     callable that takes 1 argument: the decoded map (a :class:`dict`, or a
    ///     :class:`frozendict` when it is decoded as immutable). This callback is invoked only
    ///     for maps that used indefinite-length encoding, before ``object_hook``, and its
    ///     return value is substituted for the map (and passed to ``object_hook``, if set).
    ///     Definite-length maps never invoke it.
    /// :param semantic_decoders:
    ///     An optional mapping for overriding the decoding for select semantic tags.
    ///     The value is a mapping of semantic tags (integers) to callables that take
    ///     the decoder instance as the sole argument.
    /// :param str_errors:
    ///     determines how to handle unicode decoding errors (see the `Error Handlers`_
    ///     section in the standard library documentation for details)
    /// :param read_size: minimum amount of bytes to read at once
    ///     (ignored if ``fp`` is not seekable)
    /// :param max_depth:
    ///     maximum allowed depth for nested containers
    /// :param allow_indefinite:
    ///     if :data:`False`, raise a :exc:`CBORDecodeError` when encountering an indefinite-length
    ///     string or container in the input stream
    /// :param allow_duplicate_keys:
    ///     if :data:`False`, raise a :exc:`CBORDecodeError` when a map key that has already been
    ///     decoded in the same map is encountered
    /// :param immutable:
    ///     if :data:`True`, return immutable objects (e.g. :class:`frozenset` and :class:`tuple`)
    ///     instead of mutable objects (e.g. :class:`list` and :class:`dict`)
    /// :return:
    ///     the deserialized object
    ///
    /// .. _Error Handlers: https://docs.python.org/3/library/codecs.html#error-handlers
    #[pyfunction]
    #[pyo3(signature = (
        fp,
        *,
        tag_hook = None,
        object_hook = None,
        array_hook = None,
        indefinite_string_hook = None,
        indefinite_map_hook = None,
        semantic_decoders = None,
        str_errors = "strict",
        read_size = 4096,
        max_depth = 400,
        allow_indefinite = true,
        allow_duplicate_keys = true,
        immutable = false,
    ))]
    fn load<'py>(
        py: Python<'py>,
        fp: &Bound<'py, PyAny>,
        tag_hook: Option<&Bound<'py, PyAny>>,
        object_hook: Option<&Bound<'py, PyAny>>,
        array_hook: Option<&Bound<'py, PyAny>>,
        indefinite_string_hook: Option<&Bound<'py, PyAny>>,
        indefinite_map_hook: Option<&Bound<'py, PyAny>>,
        semantic_decoders: Option<&Bound<'py, PyMapping>>,
        str_errors: &str,
        read_size: usize,
        max_depth: usize,
        allow_indefinite: bool,
        allow_duplicate_keys: bool,
        immutable: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let mut decoder = CBORDecoder::new(
            py,
            fp,
            tag_hook,
            object_hook,
            array_hook,
            indefinite_string_hook,
            indefinite_map_hook,
            semantic_decoders,
            str_errors,
            read_size,
            max_depth,
            allow_indefinite,
            allow_duplicate_keys,
        )?;
        decoder.decode(py, immutable)
    }

    /// Deserialize an object from a bytestring.
    ///
    /// :param data:
    ///     the bytestring (or any object implementing the buffer protocol) to deserialize
    ///
    ///     .. note:: Types other than :class:`bytes` will be converted to :class:`bytes`, involving
    ///               memory copying.
    /// :param tag_hook:
    ///     callable that takes 2 arguments: the decoder instance, and the :class:`.CBORTag`
    ///     to be decoded. This callback is invoked for any tags for which there is no
    ///     built-in decoder. The return value is substituted for the :class:`.CBORTag`
    ///     object in the deserialized output
    /// :param object_hook:
    ///     callable that takes 2 arguments: the decoder instance, and a dictionary. This
    ///     callback is invoked for each deserialized :class:`dict` object. The return value
    ///     is substituted for the dict in the deserialized output.
    /// :param array_hook:
    ///     callable that takes 2 arguments: the decoded array (a :class:`list`, or a
    ///     :class:`tuple` when ``immutable`` is true), and a boolean that is :data:`True` if
    ///     the array used indefinite-length encoding. This callback is invoked for each
    ///     deserialized array, and its return value is substituted for the array in the
    ///     deserialized output. It allows callers to preserve the distinction between
    ///     definite- and indefinite-length arrays, which is otherwise lost after decoding.
    /// :param indefinite_string_hook:
    ///     callable that takes 2 arguments: the decoded string (a :class:`bytes` for a byte
    ///     string, or a :class:`str` for a text string), and a :class:`tuple` holding the
    ///     length in bytes of each chunk, in encoding order. This callback is invoked only for
    ///     strings that used indefinite-length encoding, and its return value is substituted
    ///     for the string in the deserialized output. Definite-length strings never invoke it.
    /// :param indefinite_map_hook:
    ///     callable that takes 1 argument: the decoded map (a :class:`dict`, or a
    ///     :class:`frozendict` when it is decoded as immutable). This callback is invoked only
    ///     for maps that used indefinite-length encoding, before ``object_hook``, and its
    ///     return value is substituted for the map (and passed to ``object_hook``, if set).
    ///     Definite-length maps never invoke it.
    /// :param semantic_decoders:
    ///     An optional mapping for overriding the decoding for select semantic tags.
    ///     The value is a mapping of semantic tags (integers) to callables that take
    ///     the decoder instance as the sole argument.
    /// :param str_errors:
    ///     determines how to handle unicode decoding errors (see the `Error Handlers`_
    ///     section in the standard library documentation for details)
    /// :param max_depth:
    ///     maximum allowed depth for nested containers
    /// :param allow_indefinite:
    ///     if :data:`False`, raise a :exc:`CBORDecodeError` when encountering an indefinite-length
    ///     string or container in the input stream
    /// :param allow_duplicate_keys:
    ///     if :data:`False`, raise a :exc:`CBORDecodeError` when a map key that has already been
    ///     decoded in the same map is encountered
    /// :param immutable:
    ///     if :data:`True`, return immutable objects (e.g. :class:`frozenset` and :class:`tuple`)
    ///     instead of mutable objects (e.g. :class:`list` and :class:`dict`)
    /// :return:
    ///     the deserialized object
    ///
    /// .. _Error Handlers: https://docs.python.org/3/library/codecs.html#error-handlers
    #[pyfunction]
    #[pyo3(signature = (
        data,
        *,
        tag_hook = None,
        object_hook = None,
        array_hook = None,
        indefinite_string_hook = None,
        indefinite_map_hook = None,
        semantic_decoders = None,
        str_errors = "strict",
        max_depth = 400,
        allow_indefinite = true,
        allow_duplicate_keys = true,
        immutable = false,
    ))]
    fn loads<'py>(
        py: Python<'py>,
        data: &Bound<'py, PyAny>,
        tag_hook: Option<&Bound<'py, PyAny>>,
        object_hook: Option<&Bound<'py, PyAny>>,
        array_hook: Option<&Bound<'py, PyAny>>,
        indefinite_string_hook: Option<&Bound<'py, PyAny>>,
        indefinite_map_hook: Option<&Bound<'py, PyAny>>,
        semantic_decoders: Option<&Bound<'py, PyMapping>>,
        str_errors: &str,
        max_depth: usize,
        allow_indefinite: bool,
        allow_duplicate_keys: bool,
        immutable: bool,
    ) -> PyResult<Bound<'py, PyAny>> {
        let bytes = if let Ok(bytes) = data.cast::<PyBytes>() {
            bytes.clone()
        } else if let Ok(pybuf) = PyBuffer::<u8>::get(data) {
            PyBytes::new_with(py, pybuf.item_count(), |target| {
                pybuf.copy_to_slice(py, target)
            })?
        } else {
            return Err(PyTypeError::new_err(format!(
                "a bytes-like object is required, not '{}'",
                data.get_type().qualname()?
            )));
        };

        let mut decoder = CBORDecoder::new_internal(
            py,
            None,
            Some(bytes),
            tag_hook,
            object_hook,
            array_hook,
            indefinite_string_hook,
            indefinite_map_hook,
            semantic_decoders,
            str_errors,
            0,
            max_depth,
            allow_indefinite,
            allow_duplicate_keys,
        )?;
        decoder.decode(py, immutable)
    }

    #[pymodule_init]
    fn init(m: &Bound<'_, PyModule>) -> PyResult<()> {
        let py = m.py();

        BREAK_MARKER.get_or_try_init(py, || {
            py.import("builtins")?
                .getattr("object")?
                .call0()
                .map(Bound::unbind)
        })?;
        SYS_MAXSIZE.get_or_try_init(py, || py.import("sys")?.getattr("maxsize")?.extract())?;

        Ok(())
    }
}
