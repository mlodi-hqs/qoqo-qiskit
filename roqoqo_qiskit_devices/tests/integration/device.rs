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

use ndarray::array;

use roqoqo::devices::QoqoDevice;
use roqoqo_qiskit_devices::*;

use test_case::test_case;

#[test_case(IBMDevice::from(IBMBelemDevice::new()); "BelemDevice")]
#[test_case(IBMDevice::from(IBMJakartaDevice::new()); "JakartaDevice")]
#[test_case(IBMDevice::from(IBMLagosDevice::new()); "LagosDevice")]
#[test_case(IBMDevice::from(IBMLimaDevice::new()); "LimaDevice")]
#[test_case(IBMDevice::from(IBMManilaDevice::new()); "ManilaDevice")]
#[test_case(IBMDevice::from(IBMNairobiDevice::new()); "NairobiDevice")]
#[test_case(IBMDevice::from(IBMPerthDevice::new()); "PerthDevice")]
#[test_case(IBMDevice::from(IBMQuitoDevice::new()); "QuitoDevice")]
fn test_single_qubit_gate_time(device: IBMDevice) {
    assert_eq!(device.single_qubit_gate_time("PauliX", &0), None);
}

#[test_case(IBMDevice::from(IBMBelemDevice::new()); "BelemDevice")]
#[test_case(IBMDevice::from(IBMJakartaDevice::new()); "JakartaDevice")]
#[test_case(IBMDevice::from(IBMLagosDevice::new()); "LagosDevice")]
#[test_case(IBMDevice::from(IBMLimaDevice::new()); "LimaDevice")]
#[test_case(IBMDevice::from(IBMManilaDevice::new()); "ManilaDevice")]
#[test_case(IBMDevice::from(IBMNairobiDevice::new()); "NairobiDevice")]
#[test_case(IBMDevice::from(IBMPerthDevice::new()); "PerthDevice")]
#[test_case(IBMDevice::from(IBMQuitoDevice::new()); "QuitoDevice")]
fn test_set_single_qubit_gate_time(mut device: IBMDevice) {
    assert!(device.set_single_qubit_gate_time("PauliX", 0, 0.5).is_ok());
    assert_eq!(device.single_qubit_gate_time("PauliX", &0).unwrap(), 0.5);
}

#[test_case(IBMDevice::from(IBMBelemDevice::new()); "BelemDevice")]
#[test_case(IBMDevice::from(IBMJakartaDevice::new()); "JakartaDevice")]
#[test_case(IBMDevice::from(IBMLagosDevice::new()); "LagosDevice")]
#[test_case(IBMDevice::from(IBMLimaDevice::new()); "LimaDevice")]
#[test_case(IBMDevice::from(IBMManilaDevice::new()); "ManilaDevice")]
#[test_case(IBMDevice::from(IBMNairobiDevice::new()); "NairobiDevice")]
#[test_case(IBMDevice::from(IBMPerthDevice::new()); "PerthDevice")]
#[test_case(IBMDevice::from(IBMQuitoDevice::new()); "QuitoDevice")]
fn test_single_qubit_gate_names(device: IBMDevice) {
    assert_eq!(
        device.single_qubit_gate_names(),
        vec![
            "PauliX".to_string(),
            "RotateZ".to_string(),
            "SqrtPauliX".to_string(),
        ]
    );
}

#[test_case(IBMDevice::from(IBMBelemDevice::new()); "BelemDevice")]
#[test_case(IBMDevice::from(IBMJakartaDevice::new()); "JakartaDevice")]
#[test_case(IBMDevice::from(IBMLagosDevice::new()); "LagosDevice")]
#[test_case(IBMDevice::from(IBMLimaDevice::new()); "LimaDevice")]
#[test_case(IBMDevice::from(IBMManilaDevice::new()); "ManilaDevice")]
#[test_case(IBMDevice::from(IBMNairobiDevice::new()); "NairobiDevice")]
#[test_case(IBMDevice::from(IBMPerthDevice::new()); "PerthDevice")]
#[test_case(IBMDevice::from(IBMQuitoDevice::new()); "QuitoDevice")]
fn test_two_qubit_gate_time(device: IBMDevice) {
    assert_eq!(device.two_qubit_gate_time("CNOT", &0, &1), None);
}

#[test_case(IBMDevice::from(IBMBelemDevice::new()); "BelemDevice")]
#[test_case(IBMDevice::from(IBMJakartaDevice::new()); "JakartaDevice")]
#[test_case(IBMDevice::from(IBMLagosDevice::new()); "LagosDevice")]
#[test_case(IBMDevice::from(IBMLimaDevice::new()); "LimaDevice")]
#[test_case(IBMDevice::from(IBMManilaDevice::new()); "ManilaDevice")]
#[test_case(IBMDevice::from(IBMNairobiDevice::new()); "NairobiDevice")]
#[test_case(IBMDevice::from(IBMPerthDevice::new()); "PerthDevice")]
#[test_case(IBMDevice::from(IBMQuitoDevice::new()); "QuitoDevice")]
fn test_set_two_qubit_gate_time(mut device: IBMDevice) {
    assert!(device.set_two_qubit_gate_time("CNOT", 0, 1, 0.5).is_ok());
    assert_eq!(device.two_qubit_gate_time("CNOT", &0, &1).unwrap(), 0.5);
}

#[test_case(IBMDevice::from(IBMBelemDevice::new()); "BelemDevice")]
#[test_case(IBMDevice::from(IBMJakartaDevice::new()); "JakartaDevice")]
#[test_case(IBMDevice::from(IBMLagosDevice::new()); "LagosDevice")]
#[test_case(IBMDevice::from(IBMLimaDevice::new()); "LimaDevice")]
#[test_case(IBMDevice::from(IBMManilaDevice::new()); "ManilaDevice")]
#[test_case(IBMDevice::from(IBMNairobiDevice::new()); "NairobiDevice")]
#[test_case(IBMDevice::from(IBMPerthDevice::new()); "PerthDevice")]
#[test_case(IBMDevice::from(IBMQuitoDevice::new()); "QuitoDevice")]
fn test_two_qubit_gate_names(device: IBMDevice) {
    assert_eq!(device.two_qubit_gate_names(), vec!["CNOT".to_string()]);
}

#[test_case(IBMDevice::from(IBMBelemDevice::new()); "BelemDevice")]
#[test_case(IBMDevice::from(IBMJakartaDevice::new()); "JakartaDevice")]
#[test_case(IBMDevice::from(IBMLagosDevice::new()); "LagosDevice")]
#[test_case(IBMDevice::from(IBMLimaDevice::new()); "LimaDevice")]
#[test_case(IBMDevice::from(IBMManilaDevice::new()); "ManilaDevice")]
#[test_case(IBMDevice::from(IBMNairobiDevice::new()); "NairobiDevice")]
#[test_case(IBMDevice::from(IBMPerthDevice::new()); "PerthDevice")]
#[test_case(IBMDevice::from(IBMQuitoDevice::new()); "QuitoDevice")]
fn test_three_qubit_gate_time(device: IBMDevice) {
    assert_eq!(
        device.three_qubit_gate_time("ControlledControlledPauliZ", &0, &1, &2),
        None
    );
}

#[test_case(IBMDevice::from(IBMBelemDevice::new()); "BelemDevice")]
#[test_case(IBMDevice::from(IBMJakartaDevice::new()); "JakartaDevice")]
#[test_case(IBMDevice::from(IBMLagosDevice::new()); "LagosDevice")]
#[test_case(IBMDevice::from(IBMLimaDevice::new()); "LimaDevice")]
#[test_case(IBMDevice::from(IBMManilaDevice::new()); "ManilaDevice")]
#[test_case(IBMDevice::from(IBMNairobiDevice::new()); "NairobiDevice")]
#[test_case(IBMDevice::from(IBMPerthDevice::new()); "PerthDevice")]
#[test_case(IBMDevice::from(IBMQuitoDevice::new()); "QuitoDevice")]
fn test_multi_qubit_gate_time(device: IBMDevice) {
    assert_eq!(
        device.multi_qubit_gate_time("MultiQubitZZ", &[0, 1, 2]),
        None
    );
}

#[test_case(IBMDevice::from(IBMBelemDevice::new()); "BelemDevice")]
#[test_case(IBMDevice::from(IBMJakartaDevice::new()); "JakartaDevice")]
#[test_case(IBMDevice::from(IBMLagosDevice::new()); "LagosDevice")]
#[test_case(IBMDevice::from(IBMLimaDevice::new()); "LimaDevice")]
#[test_case(IBMDevice::from(IBMManilaDevice::new()); "ManilaDevice")]
#[test_case(IBMDevice::from(IBMNairobiDevice::new()); "NairobiDevice")]
#[test_case(IBMDevice::from(IBMPerthDevice::new()); "PerthDevice")]
#[test_case(IBMDevice::from(IBMQuitoDevice::new()); "QuitoDevice")]
fn test_multi_qubit_gate_names(device: IBMDevice) {
    assert!(device.multi_qubit_gate_names().is_empty());
}

#[test_case(IBMDevice::from(IBMBelemDevice::new()); "BelemDevice")]
#[test_case(IBMDevice::from(IBMJakartaDevice::new()); "JakartaDevice")]
#[test_case(IBMDevice::from(IBMLagosDevice::new()); "LagosDevice")]
#[test_case(IBMDevice::from(IBMLimaDevice::new()); "LimaDevice")]
#[test_case(IBMDevice::from(IBMManilaDevice::new()); "ManilaDevice")]
#[test_case(IBMDevice::from(IBMNairobiDevice::new()); "NairobiDevice")]
#[test_case(IBMDevice::from(IBMPerthDevice::new()); "PerthDevice")]
#[test_case(IBMDevice::from(IBMQuitoDevice::new()); "QuitoDevice")]
fn test_qubit_decoherence_rates(device: IBMDevice) {
    assert_eq!(device.qubit_decoherence_rates(&0), None);
}

#[test_case(IBMDevice::from(IBMBelemDevice::new()), 5; "BelemDevice")]
#[test_case(IBMDevice::from(IBMJakartaDevice::new()), 7; "JakartaDevice")]
#[test_case(IBMDevice::from(IBMLagosDevice::new()), 7; "LagosDevice")]
#[test_case(IBMDevice::from(IBMLimaDevice::new()), 5; "LimaDevice")]
#[test_case(IBMDevice::from(IBMManilaDevice::new()), 5; "ManilaDevice")]
#[test_case(IBMDevice::from(IBMNairobiDevice::new()), 7; "NairobiDevice")]
#[test_case(IBMDevice::from(IBMPerthDevice::new()), 7; "PerthDevice")]
#[test_case(IBMDevice::from(IBMQuitoDevice::new()), 5; "QuitoDevice")]
fn test_number_qubits(device: IBMDevice, qubits: usize) {
    assert_eq!(device.number_qubits(), qubits);
}

#[test_case(IBMDevice::from(IBMBelemDevice::new()); "BelemDevice")]
#[test_case(IBMDevice::from(IBMJakartaDevice::new()); "JakartaDevice")]
#[test_case(IBMDevice::from(IBMLagosDevice::new()); "LagosDevice")]
#[test_case(IBMDevice::from(IBMLimaDevice::new()); "LimaDevice")]
#[test_case(IBMDevice::from(IBMManilaDevice::new()); "ManilaDevice")]
#[test_case(IBMDevice::from(IBMNairobiDevice::new()); "NairobiDevice")]
#[test_case(IBMDevice::from(IBMPerthDevice::new()); "PerthDevice")]
#[test_case(IBMDevice::from(IBMQuitoDevice::new()); "QuitoDevice")]
fn test_add_damping(mut device: IBMDevice) {
    device.add_damping(0, 0.5).unwrap();
    assert_eq!(
        device.qubit_decoherence_rates(&0).unwrap(),
        array![[0.5, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    )
}

#[test_case(IBMDevice::from(IBMBelemDevice::new()); "BelemDevice")]
#[test_case(IBMDevice::from(IBMJakartaDevice::new()); "JakartaDevice")]
#[test_case(IBMDevice::from(IBMLagosDevice::new()); "LagosDevice")]
#[test_case(IBMDevice::from(IBMLimaDevice::new()); "LimaDevice")]
#[test_case(IBMDevice::from(IBMManilaDevice::new()); "ManilaDevice")]
#[test_case(IBMDevice::from(IBMNairobiDevice::new()); "NairobiDevice")]
#[test_case(IBMDevice::from(IBMPerthDevice::new()); "PerthDevice")]
#[test_case(IBMDevice::from(IBMQuitoDevice::new()); "QuitoDevice")]
fn test_add_dephasing(mut device: IBMDevice) {
    device.add_dephasing(0, 0.5).unwrap();
    assert_eq!(
        device.qubit_decoherence_rates(&0).unwrap(),
        array![[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.5]]
    )
}

#[test_case(IBMDevice::from(IBMBelemDevice::new()); "BelemDevice")]
#[test_case(IBMDevice::from(IBMJakartaDevice::new()); "JakartaDevice")]
#[test_case(IBMDevice::from(IBMLagosDevice::new()); "LagosDevice")]
#[test_case(IBMDevice::from(IBMLimaDevice::new()); "LimaDevice")]
#[test_case(IBMDevice::from(IBMManilaDevice::new()); "ManilaDevice")]
#[test_case(IBMDevice::from(IBMNairobiDevice::new()); "NairobiDevice")]
#[test_case(IBMDevice::from(IBMPerthDevice::new()); "PerthDevice")]
#[test_case(IBMDevice::from(IBMQuitoDevice::new()); "QuitoDevice")]
fn test_longest_chain(device: IBMDevice) {
    assert!(!device.longest_chains().is_empty());
}

#[test_case(IBMDevice::from(IBMBelemDevice::new()); "BelemDevice")]
#[test_case(IBMDevice::from(IBMJakartaDevice::new()); "JakartaDevice")]
#[test_case(IBMDevice::from(IBMLagosDevice::new()); "LagosDevice")]
#[test_case(IBMDevice::from(IBMLimaDevice::new()); "LimaDevice")]
#[test_case(IBMDevice::from(IBMManilaDevice::new()); "ManilaDevice")]
#[test_case(IBMDevice::from(IBMNairobiDevice::new()); "NairobiDevice")]
#[test_case(IBMDevice::from(IBMPerthDevice::new()); "PerthDevice")]
#[test_case(IBMDevice::from(IBMQuitoDevice::new()); "QuitoDevice")]
fn test_longest_closed_chain(device: IBMDevice) {
    assert!(device.longest_closed_chains().is_empty());
}

#[test_case(IBMDevice::from(IBMBelemDevice::new()); "BelemDevice")]
#[test_case(IBMDevice::from(IBMJakartaDevice::new()); "JakartaDevice")]
#[test_case(IBMDevice::from(IBMLagosDevice::new()); "LagosDevice")]
#[test_case(IBMDevice::from(IBMLimaDevice::new()); "LimaDevice")]
#[test_case(IBMDevice::from(IBMManilaDevice::new()); "ManilaDevice")]
#[test_case(IBMDevice::from(IBMNairobiDevice::new()); "NairobiDevice")]
#[test_case(IBMDevice::from(IBMPerthDevice::new()); "PerthDevice")]
#[test_case(IBMDevice::from(IBMQuitoDevice::new()); "QuitoDevice")]
fn test_edges(device: IBMDevice) {
    assert!(!device.two_qubit_edges().is_empty());
}
