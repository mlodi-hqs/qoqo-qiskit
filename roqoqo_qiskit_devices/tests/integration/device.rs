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

use roqoqo::devices::{Device, QoqoDevice};
use roqoqo_qiskit_devices::*;
// use roqoqo_qiskit_devices::IBMDevice::*;

use test_case::test_case;

#[test_case(IBMDevice::from(IBMBelemDevice::new()); "BelemDevice")]
#[test_case(IBMDevice::from(IBMJakartaDevice::new()); "JakartaDevice")]
#[test_case(IBMDevice::from(IBMLagosDevice::new()); "LagosDevice")]
#[test_case(IBMDevice::from(IBMLimaDevice::new()); "LimaDevice")]
#[test_case(IBMDevice::from(IBMManilaDevice::new()); "ManilaDevice")]
#[test_case(IBMDevice::from(IBMNairobiDevice::new()); "NairobiDevice")]
#[test_case(IBMDevice::from(IBMPerthDevice::new()); "PerthDevice")]
#[test_case(IBMDevice::from(IBMQuitoDevice::new()); "QuitoDevice")]
fn test_default(device: IBMDevice) {
    match device {
        IBMDevice::IBMLagosDevice(x) => assert_eq!(x, IBMLagosDevice::default()),
        IBMDevice::IBMNairobiDevice(x) => assert_eq!(x, IBMNairobiDevice::default()),
        IBMDevice::IBMPerthDevice(x) => assert_eq!(x, IBMPerthDevice::default()),
        IBMDevice::IBMBelemDevice(x) => assert_eq!(x, IBMBelemDevice::default()),
        IBMDevice::IBMJakartaDevice(x) => assert_eq!(x, IBMJakartaDevice::default()),
        IBMDevice::IBMLimaDevice(x) => assert_eq!(x, IBMLimaDevice::default()),
        IBMDevice::IBMManilaDevice(x) => assert_eq!(x, IBMManilaDevice::default()),
        IBMDevice::IBMQuitoDevice(x) => assert_eq!(x, IBMQuitoDevice::default()),
    }
}

#[test_case(IBMDevice::from(IBMBelemDevice::new()); "BelemDevice")]
#[test_case(IBMDevice::from(IBMJakartaDevice::new()); "JakartaDevice")]
#[test_case(IBMDevice::from(IBMLagosDevice::new()); "LagosDevice")]
#[test_case(IBMDevice::from(IBMLimaDevice::new()); "LimaDevice")]
#[test_case(IBMDevice::from(IBMManilaDevice::new()); "ManilaDevice")]
#[test_case(IBMDevice::from(IBMNairobiDevice::new()); "NairobiDevice")]
#[test_case(IBMDevice::from(IBMPerthDevice::new()); "PerthDevice")]
#[test_case(IBMDevice::from(IBMQuitoDevice::new()); "QuitoDevice")]
fn test_from(device: IBMDevice) {
    match device {
        IBMDevice::IBMLagosDevice(x) => _ = IBMDevice::from(&x),
        IBMDevice::IBMNairobiDevice(x) => _ = IBMDevice::from(&x),
        IBMDevice::IBMPerthDevice(x) => _ = IBMDevice::from(&x),
        IBMDevice::IBMBelemDevice(x) => _ = IBMDevice::from(&x),
        IBMDevice::IBMJakartaDevice(x) => _ = IBMDevice::from(&x),
        IBMDevice::IBMLimaDevice(x) => _ = IBMDevice::from(&x),
        IBMDevice::IBMManilaDevice(x) => _ = IBMDevice::from(&x),
        IBMDevice::IBMQuitoDevice(x) => _ = IBMDevice::from(&x),
    }
}

#[test_case(IBMDevice::from(IBMBelemDevice::new()), "ibmq_belem"; "BelemDevice")]
#[test_case(IBMDevice::from(IBMJakartaDevice::new()), "ibmq_jakarta"; "JakartaDevice")]
#[test_case(IBMDevice::from(IBMLagosDevice::new()), "ibm_lagos"; "LagosDevice")]
#[test_case(IBMDevice::from(IBMLimaDevice::new()), "ibmq_lima"; "LimaDevice")]
#[test_case(IBMDevice::from(IBMManilaDevice::new()), "ibmq_manila"; "ManilaDevice")]
#[test_case(IBMDevice::from(IBMNairobiDevice::new()), "ibm_nairobi"; "NairobiDevice")]
#[test_case(IBMDevice::from(IBMPerthDevice::new()), "ibm_perth"; "PerthDevice")]
#[test_case(IBMDevice::from(IBMQuitoDevice::new()), "ibmq_quito"; "QuitoDevice")]
fn test_device_name(device: IBMDevice, name: &str) {
    assert_eq!(device.name(), name);
}

#[test_case(IBMDevice::from(IBMBelemDevice::new()); "BelemDevice")]
#[test_case(IBMDevice::from(IBMJakartaDevice::new()); "JakartaDevice")]
#[test_case(IBMDevice::from(IBMLagosDevice::new()); "LagosDevice")]
#[test_case(IBMDevice::from(IBMLimaDevice::new()); "LimaDevice")]
#[test_case(IBMDevice::from(IBMManilaDevice::new()); "ManilaDevice")]
#[test_case(IBMDevice::from(IBMNairobiDevice::new()); "NairobiDevice")]
#[test_case(IBMDevice::from(IBMPerthDevice::new()); "PerthDevice")]
#[test_case(IBMDevice::from(IBMQuitoDevice::new()); "QuitoDevice")]
fn test_single_qubit_gate_time(device: IBMDevice) {
    assert_eq!(device.single_qubit_gate_time("PauliX", &0), 1.0.into());
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
    assert!(device.set_single_qubit_gate_time("PauliX", 0, 0.2).is_ok());
    assert_eq!(device.single_qubit_gate_time("PauliX", &0).unwrap(), 0.2);

    assert!(device
        .set_single_qubit_gate_time("PauliZ", 34, 0.0)
        .is_err());
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
    assert_eq!(device.two_qubit_gate_time("CNOT", &0, &1), 1.0.into());
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
    // Correct setters
    assert!(device.set_two_qubit_gate_time("CNOT", 0, 1, 0.5).is_ok());
    assert_eq!(device.two_qubit_gate_time("CNOT", &0, &1).unwrap(), 0.5);
    assert!(device.set_two_qubit_gate_time("CNOT", 0, 1, 0.2).is_ok());
    assert_eq!(device.two_qubit_gate_time("CNOT", &0, &1).unwrap(), 0.2);

    // Qubit's value too big
    assert!(device.set_two_qubit_gate_time("CNOT", 0, 12, 0.3).is_err());
    assert!(device.set_two_qubit_gate_time("CNOT", 11, 3, 0.4).is_err());

    // Unconnected qubits
    assert!(device.set_two_qubit_gate_time("CNOT", 0, 4, 0.8).is_err());
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
    );

    assert!(device.add_damping(13, 0.2).is_err());
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
    );

    assert!(device.add_dephasing(13, 0.2).is_err());
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
    // If there are no closed chains bigger than 2, this checks that
    //  nothing is missing from the hard-coded chains and edges.
    assert!(device.longest_closed_chains().iter().all(|lcc_el| {
        device
            .two_qubit_edges()
            .iter()
            .any(|edge| edge.0 == lcc_el[0] && edge.1 == lcc_el[1])
            || device
                .two_qubit_edges()
                .iter()
                .any(|edge| edge.1 == lcc_el[0] && edge.0 == lcc_el[1])
    }));
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

#[test_case(IBMDevice::from(IBMBelemDevice::new()); "BelemDevice")]
#[test_case(IBMDevice::from(IBMJakartaDevice::new()); "JakartaDevice")]
#[test_case(IBMDevice::from(IBMLagosDevice::new()); "LagosDevice")]
#[test_case(IBMDevice::from(IBMLimaDevice::new()); "LimaDevice")]
#[test_case(IBMDevice::from(IBMManilaDevice::new()); "ManilaDevice")]
#[test_case(IBMDevice::from(IBMNairobiDevice::new()); "NairobiDevice")]
#[test_case(IBMDevice::from(IBMPerthDevice::new()); "PerthDevice")]
#[test_case(IBMDevice::from(IBMQuitoDevice::new()); "QuitoDevice")]
fn test_to_generic_device(device: IBMDevice) {
    let created_generic = device.to_generic_device().unwrap();
    assert_eq!(device.number_qubits(), created_generic.number_qubits());
    let mut ibm_single_sorted = device.single_qubit_gate_names();
    ibm_single_sorted.sort();
    let mut generic_single_sorted = created_generic.single_qubit_gate_names();
    generic_single_sorted.sort();
    assert!(ibm_single_sorted == generic_single_sorted);
    for i in 0..device.number_qubits() {
        for gate in device.single_qubit_gate_names() {
            assert_eq!(
                device.single_qubit_gate_time(gate.as_str(), &i),
                created_generic.single_qubit_gate_time(gate.as_str(), &i)
            );
        }
        assert_eq!(
            device.qubit_decoherence_rates(&i),
            created_generic.qubit_decoherence_rates(&i)
        );
    }
    let mut ibm_two_sorted = device.two_qubit_gate_names();
    ibm_two_sorted.sort();
    let mut generic_two_sorted = created_generic.two_qubit_gate_names();
    generic_two_sorted.sort();
    assert!(ibm_two_sorted == generic_two_sorted);
    for gate in device.two_qubit_gate_names() {
        for i in 0..device.number_qubits() - 1 {
            for j in 1..device.number_qubits() {
                assert_eq!(
                    device.two_qubit_gate_time(gate.as_str(), &i, &j),
                    created_generic.two_qubit_gate_time(gate.as_str(), &i, &j)
                );
            }
        }
    }
    assert_eq!(
        device.multi_qubit_gate_names(),
        created_generic.multi_qubit_gate_names()
    );
    assert_eq!(device.two_qubit_edges(), created_generic.two_qubit_edges());
}
