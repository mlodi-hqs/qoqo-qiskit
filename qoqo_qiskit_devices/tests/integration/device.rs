// Copyright © 2023-2025 HQS Quantum Simulations GmbH. All Rights Reserved.
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

use qoqo::devices::GenericDeviceWrapper;
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
        let single_qubit_gates = device
            .call_method0(py, "single_qubit_gate_names")
            .unwrap()
            .extract::<Vec<String>>(py)
            .unwrap();
        assert!(single_qubit_gates.contains(&"PauliX".to_string()));
        assert!(single_qubit_gates.contains(&"SqrtPauliX".to_string()));
        assert!(single_qubit_gates.contains(&"RotateZ".to_string()));
        assert!(single_qubit_gates.contains(&"Identity".to_string()));

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

/// Test single-qubit and two-qubit gates times setters and getters
#[test_case(new_device(IBMDevice::from(IBMBelemDevice::new())); "belem")]
#[test_case(new_device(IBMDevice::from(IBMNairobiDevice::new())); "nairobi")]
#[test_case(new_device(IBMDevice::from(IBMJakartaDevice::new())); "jakarta")]
#[test_case(new_device(IBMDevice::from(IBMLagosDevice::new())); "lagos")]
#[test_case(new_device(IBMDevice::from(IBMLimaDevice::new())); "lima")]
#[test_case(new_device(IBMDevice::from(IBMManilaDevice::new())); "manila")]
#[test_case(new_device(IBMDevice::from(IBMPerthDevice::new())); "perth")]
#[test_case(new_device(IBMDevice::from(IBMQuitoDevice::new())); "quito")]
fn test_gate_timings(device: Py<PyAny>) {
    pyo3::prepare_freethreaded_python();
    Python::with_gil(|py| {
        device
            .call_method1(py, "set_single_qubit_gate_time", ("PauliX", 0, 0.5))
            .unwrap();
        let single_qubit_time = device
            .call_method1(py, "single_qubit_gate_time", ("PauliX", 0))
            .unwrap()
            .extract::<f64>(py)
            .unwrap();
        assert_eq!(single_qubit_time, 0.5);

        device
            .call_method1(py, "set_two_qubit_gate_time", ("CNOT", 0, 1, 0.5))
            .unwrap();
        let two_qubit_time = device
            .call_method1(py, "two_qubit_gate_time", ("CNOT", 0, 1))
            .unwrap()
            .extract::<f64>(py)
            .unwrap();
        assert_eq!(two_qubit_time, 0.5);
    });
}

/// Test add_damping, add_dephasing, decoherence methods
#[test_case(new_device(IBMDevice::from(IBMBelemDevice::new())); "belem")]
#[test_case(new_device(IBMDevice::from(IBMNairobiDevice::new())); "nairobi")]
#[test_case(new_device(IBMDevice::from(IBMJakartaDevice::new())); "jakarta")]
#[test_case(new_device(IBMDevice::from(IBMLagosDevice::new())); "lagos")]
#[test_case(new_device(IBMDevice::from(IBMLimaDevice::new())); "lima")]
#[test_case(new_device(IBMDevice::from(IBMManilaDevice::new())); "manila")]
#[test_case(new_device(IBMDevice::from(IBMPerthDevice::new())); "perth")]
#[test_case(new_device(IBMDevice::from(IBMQuitoDevice::new())); "quito")]
fn test_damping_dephasing_decoherence(device: Py<PyAny>) {
    pyo3::prepare_freethreaded_python();
    Python::with_gil(|py| {
        device.call_method1(py, "add_damping", (0, 0.5)).unwrap();
        device.call_method1(py, "add_dephasing", (0, 0.2)).unwrap();
        let rates = device
            .call_method1(py, "qubit_decoherence_rates", (0,))
            .unwrap()
            .extract::<Vec<Vec<f64>>>(py)
            .unwrap();
        assert_eq!(
            rates,
            vec![
                vec![0.5, 0.0, 0.0],
                vec![0.0, 0.0, 0.0],
                vec![0.0, 0.0, 0.2]
            ]
        )
    });
}

/// Test single_qubit_gate_names and two_qubit_gate_names functions of the devices
#[test_case(IBMDevice::from(IBMBelemDevice::new()), new_device(IBMDevice::from(IBMBelemDevice::new())); "belem")]
#[test_case(IBMDevice::from(IBMNairobiDevice::new()), new_device(IBMDevice::from(IBMNairobiDevice::new())); "nairobi")]
#[test_case(IBMDevice::from(IBMJakartaDevice::new()), new_device(IBMDevice::from(IBMJakartaDevice::new())); "jakarta")]
#[test_case(IBMDevice::from(IBMLagosDevice::new()), new_device(IBMDevice::from(IBMLagosDevice::new())); "lagos")]
#[test_case(IBMDevice::from(IBMLimaDevice::new()), new_device(IBMDevice::from(IBMLimaDevice::new())); "lima")]
#[test_case(IBMDevice::from(IBMManilaDevice::new()), new_device(IBMDevice::from(IBMManilaDevice::new())); "manila")]
#[test_case(IBMDevice::from(IBMPerthDevice::new()), new_device(IBMDevice::from(IBMPerthDevice::new())); "perth")]
#[test_case(IBMDevice::from(IBMQuitoDevice::new()), new_device(IBMDevice::from(IBMQuitoDevice::new())); "quito")]
fn test_to_generic_device(device: IBMDevice, pyo3_device: Py<PyAny>) {
    pyo3::prepare_freethreaded_python();
    Python::with_gil(|py| {
        let result = pyo3_device
            .call_method0(py, "to_generic_device")
            .unwrap()
            .extract::<GenericDeviceWrapper>(py)
            .unwrap();

        let rust_result: GenericDeviceWrapper = GenericDeviceWrapper {
            internal: device.to_generic_device().unwrap(),
        };
        assert_eq!(result, rust_result);
    })
}

/// Test qoqo_qiskit_device_from_ibmq_identifier method
#[test_case("ibmq_belem", new_device(IBMDevice::from(IBMBelemDevice::new())); "belem")]
#[test_case("ibm_nairobi", new_device(IBMDevice::from(IBMNairobiDevice::new())); "nairobi")]
#[test_case("ibmq_jakarta", new_device(IBMDevice::from(IBMJakartaDevice::new())); "jakarta")]
#[test_case("ibm_lagos", new_device(IBMDevice::from(IBMLagosDevice::new())); "lagos")]
#[test_case("ibmq_lima", new_device(IBMDevice::from(IBMLimaDevice::new())); "lima")]
#[test_case("ibmq_manila", new_device(IBMDevice::from(IBMManilaDevice::new())); "manila")]
#[test_case("ibm_perth", new_device(IBMDevice::from(IBMPerthDevice::new())); "perth")]
#[test_case("ibmq_quito", new_device(IBMDevice::from(IBMQuitoDevice::new())); "quito")]
fn test_initialization_from_identifier(name: &str, device: Py<PyAny>) {
    pyo3::prepare_freethreaded_python();
    Python::with_gil(|py| {
        let device_type = device.as_ref(py).get_type();
        let result = qoqo_qiskit_device_from_ibmq_identifier(name).unwrap();
        let resulting_type = result.as_ref(py).get_type();
        assert!(device_type.compare(resulting_type).is_ok());
    })
}
