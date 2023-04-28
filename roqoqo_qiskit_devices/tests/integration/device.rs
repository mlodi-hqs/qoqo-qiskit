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

use roqoqo::devices::Device;
use roqoqo_qiskit_devices::*;

use test_case::test_case;


#[test_case(IBMDevice::from(IBMBelemDevice::new()); "BelemDevice")]
#[test_case(IBMDevice::from(IBMJakartaDevice::new()); "JakartaDevice")]
#[test_case(IBMDevice::from(IBMLagosDevice::new()); "LagosDevice")]
#[test_case(IBMDevice::from(IBMLimaDevice::new()); "LimaDevice")]
#[test_case(IBMDevice::from(IBMManilaDevice::new()); "ManilaDevice")]
#[test_case(IBMDevice::from(IBMNairobiDevice::new()); "NairobiDevice")]
#[test_case(IBMDevice::from(IBMOsloDevice::new()); "OsloDevice")]
#[test_case(IBMDevice::from(IBMPerthDevice::new()); "PerthDevice")]
#[test_case(IBMDevice::from(IBMQuitoDevice::new()); "QuitoDevice")]
fn test_single_qubit_gate_time(device: IBMDevice) {
    assert_eq!(device.single_qubit_gate_time("PauliX", &0).unwrap(), 0.0);
}

#[test_case(IBMDevice::from(IBMBelemDevice::new()); "BelemDevice")]
#[test_case(IBMDevice::from(IBMJakartaDevice::new()); "JakartaDevice")]
#[test_case(IBMDevice::from(IBMLagosDevice::new()); "LagosDevice")]
#[test_case(IBMDevice::from(IBMLimaDevice::new()); "LimaDevice")]
#[test_case(IBMDevice::from(IBMManilaDevice::new()); "ManilaDevice")]
#[test_case(IBMDevice::from(IBMNairobiDevice::new()); "NairobiDevice")]
#[test_case(IBMDevice::from(IBMOsloDevice::new()); "OsloDevice")]
#[test_case(IBMDevice::from(IBMPerthDevice::new()); "PerthDevice")]
#[test_case(IBMDevice::from(IBMQuitoDevice::new()); "QuitoDevice")]
fn test_two_qubit_gate_time(device: IBMDevice) {
    assert_eq!(device.two_qubit_gate_time("CNOT", &0, &1).unwrap(), 0.0);
}

#[test_case(IBMDevice::from(IBMBelemDevice::new()); "BelemDevice")]
#[test_case(IBMDevice::from(IBMJakartaDevice::new()); "JakartaDevice")]
#[test_case(IBMDevice::from(IBMLagosDevice::new()); "LagosDevice")]
#[test_case(IBMDevice::from(IBMLimaDevice::new()); "LimaDevice")]
#[test_case(IBMDevice::from(IBMManilaDevice::new()); "ManilaDevice")]
#[test_case(IBMDevice::from(IBMNairobiDevice::new()); "NairobiDevice")]
#[test_case(IBMDevice::from(IBMOsloDevice::new()); "OsloDevice")]
#[test_case(IBMDevice::from(IBMPerthDevice::new()); "PerthDevice")]
#[test_case(IBMDevice::from(IBMQuitoDevice::new()); "QuitoDevice")]
fn test_three_qubit_gate_time(device: IBMDevice) {
    assert_eq!(device.three_qubit_gate_time("ControlledControlledPauliZ", &0, &1, &2).unwrap(), 0.0);
}

#[test_case(IBMDevice::from(IBMBelemDevice::new()); "BelemDevice")]
#[test_case(IBMDevice::from(IBMJakartaDevice::new()); "JakartaDevice")]
#[test_case(IBMDevice::from(IBMLagosDevice::new()); "LagosDevice")]
#[test_case(IBMDevice::from(IBMLimaDevice::new()); "LimaDevice")]
#[test_case(IBMDevice::from(IBMManilaDevice::new()); "ManilaDevice")]
#[test_case(IBMDevice::from(IBMNairobiDevice::new()); "NairobiDevice")]
#[test_case(IBMDevice::from(IBMOsloDevice::new()); "OsloDevice")]
#[test_case(IBMDevice::from(IBMPerthDevice::new()); "PerthDevice")]
#[test_case(IBMDevice::from(IBMQuitoDevice::new()); "QuitoDevice")]
fn test_multi_qubit_gate_time(device: IBMDevice) {
    assert_eq!(device.multi_qubit_gate_time("MultiQubitZZ", &[0, 1, 2]).unwrap(), 0.0);
}
