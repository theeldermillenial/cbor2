use crate::utils::PyImportable;
use pyo3::import_exception;

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
