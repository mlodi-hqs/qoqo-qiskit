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

mod ibm_belem;
pub use ibm_belem::*;

mod ibm_jakarta;
pub use ibm_jakarta::*;

mod ibm_lagos;
pub use ibm_lagos::*;

mod ibm_lima;
pub use ibm_lima::*;

mod ibm_manila;
pub use ibm_manila::*;

mod ibm_nairobi;
pub use ibm_nairobi::*;

mod ibm_oslo;
pub use ibm_oslo::*;

mod ibm_perth;
pub use ibm_perth::*;

mod ibm_quito;
pub use ibm_quito::*;

use pyo3::prelude::*;

/// IBM Devices
#[pymodule]
pub fn ibm_devices(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<IBMBelemDeviceWrapper>()?;
    m.add_class::<IBMJakartaDeviceWrapper>()?;
    m.add_class::<IBMLagosDeviceWrapper>()?;
    m.add_class::<IBMLimaDeviceWrapper>()?;
    m.add_class::<IBMManilaDeviceWrapper>()?;
    m.add_class::<IBMNairobiDeviceWrapper>()?;
    m.add_class::<IBMOsloDeviceWrapper>()?;
    m.add_class::<IBMPerthDeviceWrapper>()?;
    m.add_class::<IBMQuitoDeviceWrapper>()?;
    Ok(())
}
