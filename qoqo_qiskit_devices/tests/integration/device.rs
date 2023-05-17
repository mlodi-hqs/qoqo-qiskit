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
use pyo3::types::PyType;

use qoqo_qiskit_devices::*;
use roqoqo_qiskit_devices::*;

use test_case::test_case;

// helper functions
fn new_device(device: IBMDevice) -> Py<PyAny> {
    pyo3::prepare_freethreaded_python();
    Python::with_gil(|py| -> Py<PyAny> {
        let device_type: &PyType = match device {
            IBMDevice::IBMLagosDevice(_) => py.get_type::<IBMLagosDeviceWrapper>(),
            IBMDevice::IBMNairobiDevice(_) => py.get_type::<IBMNairobiDeviceWrapper>(),
            IBMDevice::IBMPerthDevice(_) => py.get_type::<IBMPerthDeviceWrapper>(),
            IBMDevice::IBMBelemDevice(_) => py.get_type::<IBMBelemDeviceWrapper>(),
            IBMDevice::IBMJakartaDevice(_) => py.get_type::<IBMJakartaDeviceWrapper>(),
            IBMDevice::IBMLimaDevice(_) => py.get_type::<IBMLimaDeviceWrapper>(),
            IBMDevice::IBMManilaDevice(_) => py.get_type::<IBMManilaDeviceWrapper>(),
            IBMDevice::IBMQuitoDevice(_) => py.get_type::<IBMQuitoDeviceWrapper>(),
        };
        device_type.call0().unwrap().into()
    })
}

/// Test single_qubit_gate_names and two_qubit_gate_names functions of the devices
#[test_case(new_device(IBMDevice::from(IBMBelemDevice::new())); "belem")]
#[test_case(new_device(IBMDevice::from(IBMNairobiDevice::new())); "nairobi")]
#[test_case(new_device(IBMDevice::from(IBMJakartaDevice::new())); "jakarta")]
#[test_case(new_device(IBMDevice::from(IBMLagosDevice::new())); "lagos")]
#[test_case(new_device(IBMDevice::from(IBMLimaDevice::new())); "lima")]
#[test_case(new_device(IBMDevice::from(IBMManilaDevice::new())); "manila")]
#[test_case(new_device(IBMDevice::from(IBMPerthDevice::new())); "perth")]
#[test_case(new_device(IBMDevice::from(IBMQuitoDevice::new())); "quito")]
fn test_gate_names(device: Py<PyAny>) {
    pyo3::prepare_freethreaded_python();
    Python::with_gil(|py| {
        let singe_qubit_gates = device
            .call_method0(py, "single_qubit_gate_names")
            .unwrap()
            .extract::<Vec<String>>(py)
            .unwrap();
        assert!(singe_qubit_gates.contains(&"PauliX".to_string()));
        assert!(singe_qubit_gates.contains(&"SqrtPauliX".to_string()));
        assert!(singe_qubit_gates.contains(&"RotateZ".to_string()));

        let two_qubit_gates = device
            .call_method0(py, "two_qubit_gate_names")
            .unwrap()
            .extract::<Vec<String>>(py)
            .unwrap();
        assert_eq!(two_qubit_gates, vec!["CNOT".to_string()]);

        let multi_qubit_gates = device
            .call_method0(py, "multi_qubit_gate_names")
            .unwrap()
            .extract::<Vec<String>>(py)
            .unwrap();
        assert_eq!(multi_qubit_gates, Vec::<String>::new());
    })
}
