# Copyright © 2023-2025 HQS Quantum Simulations GmbH.
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
"""Qoqo-qiskit utils modules for compatibility purposes."""

from typing import TYPE_CHECKING

from qiskit.quantum_info.operators import SparsePauliOp

if TYPE_CHECKING:
    from struqture_py.spins import PauliHamiltonian  # type:ignore


def struqture_hamiltonian_to_qiskit_op(
    pauli_hamiltonian: "PauliHamiltonian", n_qubits: int
) -> SparsePauliOp:
    """Converts a struqture's PauliHamiltonian instance into a qiskit's SparsePauliOp one.

    Args:
        pauli_hamiltonian (PauliHamiltonian): The struqture_py.spins.PauliHamiltonian instance.
        n_qubits (int): Total number of qubits.

    Returns:
        SparsePauliOp: The equivalent SparsePauliOp instance.
    """

    def convert_single(s: str) -> str:
        pauli_vec = ["I"] * n_qubits
        if s != "I":
            for i in range(0, len(s), 2):
                idx = int(s[i])
                op = s[i + 1]
                pauli_vec[n_qubits - idx - 1] = op
        return "".join(pauli_vec)

    pauli_strs = []
    coeffs = []
    for key, val in zip(pauli_hamiltonian.keys(), pauli_hamiltonian.values(), strict=False):
        s = str(key)
        p = convert_single(s)
        pauli_strs.append(p)
        coeffs.append(complex(val))

    return SparsePauliOp(pauli_strs, coeffs)
