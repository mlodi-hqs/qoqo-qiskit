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

from typing import Union
import types


class DeviceProperties:
    """Utility for updating the properties on an IBMDevice instance."""

    def __init__(self, device: Union[types.ModuleType, str]) -> None:
        """Initialized DeviceProperty utility.

        Args:
            device (Union[ibm_devices, str]): The qoqo_qiskit_devices instance (or name) that
                is used to get the properties from IBM.

        Raises:
            TypeError: The input is not a string or an `ibm_devices` instance.
        """
        if isinstance(device, str):
            self.properties = IBMProvider().get_backend(device).properties()
            self.name = device
        else:
            try:
                self.properties = IBMProvider().get_backend(device.name()).properties()
                self.name = device.name()
            except Exception:
                raise TypeError(
                    "The input device is not a string or is not an `ibm_devices` instance."
                )
        self.configurations = IBMProvider().get_backend(self.name).configuration()

    def update(self) -> None:
        """Updates the device information."""
        self.properties = IBMProvider().get_backend(self.name).properties(refresh=True)

    def single_qubit_gate_time(self, gate: str, qubit: int) -> float:
        """Returns the single-qubit gate time for a given gate and qubit.

        Args:
            gate (str): The input gate.
            qubit (int): The input qubit.

        Raises:
            ValueError: The input gate is not available on the device.
            ValueError: The input qubit is not available on the device.

        Returns:
            float: The gate time.
        """
        if qubit >= self.configurations.n_qubits:
            raise ValueError("The input qubit is not available on the device.")
        if gate not in self.configurations.basis_gates:
            raise ValueError("The input gate is not available on the device.")
        for entry in self.properties.gates:
            if len(entry.qubits) == 1 and entry.qubits == qubit and entry.gate == gate:
                return entry.parameters[1].value

    def two_qubit_gate_time(self, gate: str, control: int, target: int) -> float:
        """Returns the two-qubit gate time for a given gate and qubit.

        Args:
            gate (str): The input gate.
            control (int): The input control qubit.
            target (int): The input target qubit.

        Raises:
            ValueError: The input gate is not available on the device.
            ValueError: The input qubit is not available on the device.

        Returns:
            float: The gate time.
        """
        if (
            control >= self.configurations.n_qubits
            or target >= self.configurations.n_qubits
        ):
            raise ValueError("The input qubit is not available on the device.")
        if gate not in self.configurations.basis_gates:
            raise ValueError("The input gate is not available on the device.")
        for entry in self.properties.gates:
            if (
                len(entry.qubits) == 2
                and control in entry.qubits
                and target in entry.qubits
                and entry.gate == gate
            ):
                return entry.parameters[1].value
