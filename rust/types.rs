use crate::utils::PyImportable;
use pyo3::exceptions::PyTypeError;
use pyo3::types::{PyTuple, PyType, PyTypeMethods};
use pyo3::{Bound, IntoPyObjectExt, PyAny, PyErr, PyResult, Python, import_exception};

pub static DECIMAL_TYPE: PyImportable = PyImportable::new("decimal", "Decimal");
pub static FRACTION_TYPE: PyImportable = PyImportable::new("fractions", "Fraction");
pub static IPV4ADDRESS_TYPE: PyImportable = PyImportable::new("ipaddress", "IPv4Address");
pub static IPV4INTERFACE_TYPE: PyImportable = PyImportable::new("ipaddress", "IPv4Interface");
pub static IPV4NETWORK_TYPE: PyImportable = PyImportable::new("ipaddress", "IPv4Network");
pub static IPV6ADDRESS_TYPE: PyImportable = PyImportable::new("ipaddress", "IPv6Address");
pub static IPV6INTERFACE_TYPE: PyImportable = PyImportable::new("ipaddress", "IPv6Interface");
pub static IPV6NETWORK_TYPE: PyImportable = PyImportable::new("ipaddress", "IPv6Network");
pub static UUID_TYPE: PyImportable = PyImportable::new("uuid", "UUID");

// The error classes are cbor2's own, so ``except cbor2.CBORDecodeError`` catches errors
// raised by this decoder.
import_exception!(cbor2, CBORDecodeError);
import_exception!(cbor2, CBORDecodeEOF);

// cbor2's value classes. The decoder constructs these instead of defining its own, so decoded
// objects pass ``isinstance`` checks against cbor2 and re-encode with ``cbor2.dumps``.
pub static STOCK_TAG: PyImportable = PyImportable::new("cbor2", "CBORTag");
pub static STOCK_SIMPLE_VALUE: PyImportable = PyImportable::new("cbor2", "CBORSimpleValue");
pub static STOCK_UNDEFINED: PyImportable = PyImportable::new("cbor2", "undefined");
#[cfg(not(Py_3_15))]
pub static STOCK_FROZENDICT: PyImportable = PyImportable::new("cbor2", "frozendict");

/// Construct a cbor2 ``CBORTag`` through its type's ``tp_new`` slot. This is what calling the
/// class does, minus the ``type.__call__`` dispatch and the no-op ``object.__init__`` call.
pub fn new_stock_tag<'py>(
    py: Python<'py>,
    tag: u64,
    value: Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyAny>> {
    let class = STOCK_TAG
        .get(py)?
        .cast_into::<PyType>()
        .map_err(PyErr::from)?;
    let args = PyTuple::new(py, [tag.into_bound_py_any(py)?, value])?;
    let type_ptr = class.as_type_ptr();
    // SAFETY: ``type_ptr`` is a live type object (``class`` holds a reference), and ``tp_new``
    // is called with that type, a tuple of positional arguments and no keywords.
    unsafe {
        let tp_new = (*type_ptr)
            .tp_new
            .ok_or_else(|| PyTypeError::new_err("cbor2.CBORTag cannot be instantiated"))?;
        Bound::from_owned_ptr_or_err(py, tp_new(type_ptr, args.as_ptr(), std::ptr::null_mut()))
    }
}
