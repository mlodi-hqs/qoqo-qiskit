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

//! # roqoqo_qiskit_devices
//!
//! Qiskit devices' interface for roqoqo.
//!
//! Collection of IBM's qiskit devices interfaces implementing roqoqo's Device trait.

mod ibm_lagos;
pub use ibm_lagos::*;

mod ibm_nairobi;
pub use ibm_nairobi::*;

mod ibm_oslo;
pub use ibm_oslo::*;

mod ibm_perth;
pub use ibm_perth::*;

mod ibmq_belem;
pub use ibmq_belem::*;

mod ibmq_jakarta;
pub use ibmq_jakarta::*;

mod ibmq_lima;
pub use ibmq_lima::*;

mod ibmq_manila;
pub use ibmq_manila::*;

mod ibmq_quito;
pub use ibmq_quito::*;
