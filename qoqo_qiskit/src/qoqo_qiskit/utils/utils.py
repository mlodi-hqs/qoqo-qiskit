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

import re
from typing import TYPE_CHECKING

from qiskit.quantum_info.operators import SparsePauliOp

if TYPE_CHECKING:
    from struqture_py.spins import PauliHamiltonian  # type:ignore


def struqture_hamiltonian_to_qiskit_op(
    pauli_hamiltonian: "PauliHamiltonian",
    n_qubits: int,
    reverse_qubit_order: bool = True,
) -> SparsePauliOp:
    """Converts a struqture's PauliHamiltonian instance into a qiskit's SparsePauliOp one.

    Args:
        pauli_hamiltonian (PauliHamiltonian): The struqture_py.spins.PauliHamiltonian instance.
        n_qubits (int): Total number of qubits.
        reverse_qubit_order (bool): Makes Qiskit's rightmost char qubit 0 (little-endian).

    Returns:
        SparsePauliOp: The equivalent SparsePauliOp instance.
    """

    labels = []
    coeffs = []
    token_re = re.compile(r"(\d+)([XYZ])")

    for key, val in zip(pauli_hamiltonian.keys(), pauli_hamiltonian.values(), strict=False):
        s = str(key)  # e.g., '0Z', '0X1X', '10X11X'
        pauli = ["I"] * n_qubits
        if s != "I":
            for m in token_re.finditer(s):
                idx = int(m.group(1))  # site index (can be multi-digit)
                op = m.group(2)  # 'X', 'Y', or 'Z'
                q = (n_qubits - 1 - idx) if reverse_qubit_order else idx
                if not (0 <= q < n_qubits):
                    raise IndexError(
                        f"Site index {idx} (mapped to qubit {q}) out of range 0..{n_qubits - 1}"
                    )
                pauli[q] = op
        labels.append("".join(pauli))
        coeffs.append(complex(val))

    return SparsePauliOp(labels, coeffs)
