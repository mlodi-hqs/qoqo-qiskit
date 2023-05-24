"""Device information-gathering routines."""
# Copyright © 2023 HQS Quantum Simulations GmbH. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing permissions and limitations under
# the License.

from qiskit_ibm_provider import IBMProvider

import types


def set_qiskit_noise_information(device: types.ModuleType) -> types.ModuleType:
    """Sets a qoqo_qiskit_devices.ibm_devices instance noise info.

    Args:
        device (ibm_devices): The qoqo_qiskit_devices instance to update.

    Returns:
        ibm_devices: The input instance updated with qiskit's physical device info.
    """
    name = device.name()
    properties = IBMProvider().get_backend(name).properties()
    for qubit in range(device.number_qubits()):
        decoherence_rate = 1 / properties.t1(qubit=qubit)
        device.set_decoherence_rate(qubit, decoherence_rate)
        for gate in device.single_qubit_gate_names():
            device.set_single_qubit_gate_time(
                gate=gate,
                qubit=qubit,
                gate_time=properties.gate_property(
                    gate=gate, qubits=qubit, name="gate_length"
                )[0],
            )
        for edge in device.two_qubit_edges():
            for gate in device.two_qubit_gate_names():
                device.set_two_qubit_gate_time(
                    gate=gate,
                    control=edge[0],
                    target=edge[1],
                    gate_time=properties.gate_property(
                        gate=gate, qubits=[edge[0], edge[1]], name="gate_length"
                    )[0],
                )
                device.set_two_qubit_gate_time(
                    gate=gate,
                    control=edge[1],
                    target=edge[0],
                    gate_time=properties.gate_property(
                        gate=gate, qubits=[edge[1], edge[0]], name="gate_length"
                    )[0],
                )
    return device
