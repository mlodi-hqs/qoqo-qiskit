// Copyright © 2023 HQS Quantum Simulations GmbH. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
// in compliance with the License. You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software distributed under the
// License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
// express or implied. See the License for the specific language governing permissions and
// limitations under the License.

use pyo3::prelude::*;
use pyo3::exceptions::{PyTypeError, PyValueError};
use pyo3::types::PyByteArray;
use ndarray::Array2;
use numpy::{PyArray2, PyReadonlyArray2, ToPyArray};

use qoqo::devices::GenericDeviceWrapper;
use qoqo_macros::devicewrapper;
use roqoqo::devices::Device;

use bincode::{deserialize, serialize};

use roqoqo_qiskit_devices::IBMBelemDevice;

/// IBM Belem device
///
#[pyclass(name = "IBMBelemDevice", module = "ibm_devices")]
#[derive(Clone, Debug, PartialEq)]
pub struct IBMBelemDeviceWrapper {
    /// Internal storage of [roqoqo_qiskit_devices::IBMBelemDevice]
    pub internal: IBMBelemDevice,
}

#[devicewrapper]
impl IBMBelemDeviceWrapper {
    /// Create a new IBMBelemDevice instance.
    #[new]
    pub fn new() -> Self {
        Self {
            internal: IBMBelemDevice::new(),
        }
    }

    /// IBM's identifier.
    ///
    /// Returns:
    ///     str: The IBM's identifier of the Device.
    pub fn name(&self) -> &str {
        roqoqo_qiskit_devices::IBMBelemDevice::name()
    }
}

impl IBMBelemDeviceWrapper {
    /// Fallible conversion of generic python object...
    pub fn from_pyany(input: Py<PyAny>) -> PyResult<IBMBelemDevice> {
        Python::with_gil(|py| -> PyResult<IBMBelemDevice> {
            let input = input.as_ref(py);
            if let Ok(try_downcast) = input.extract::<IBMBelemDeviceWrapper>() {
                Ok(try_downcast.internal)
            } else {
                let get_bytes = input.call_method0("to_bincode")?;
                let bytes = get_bytes.extract::<Vec<u8>>()?;
                deserialize(&bytes[..]).map_err(|err| {
                    PyValueError::new_err(format!(
                        "Cannot treat input as IBMBelemDevice: {}",
                        err
                    ))
                })
            }
        })
    }
}

impl Default for IBMBelemDeviceWrapper {
    fn default() -> Self {
        Self::new()
    }
}
