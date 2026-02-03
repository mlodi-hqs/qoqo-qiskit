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
from typing import TYPE_CHECKING, Optional, Tuple, List, Dict

from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info.operators import SparsePauliOp
from qiskit_aer import Aer

if TYPE_CHECKING:
    from struqture_py.spins import PauliHamiltonian, PauliOperator, PauliProduct  # type:ignore

_TOKEN_RE = re.compile(r"(\d+)([XYZ])")


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


def measure_spin_operator_to_qiskit(
    input_operator: "PauliHamiltonian",
    name: str,
    undo_basis_rotation: bool,
    constant_circuit: Optional[QuantumCircuit] = None,
    number_measurements: Optional[int] = None,
    qubit_mapping: Optional[dict[int, int]] = None,
    definitionbit_length: Optional[int] = None,
) -> Tuple[list[QuantumCircuit], int]:
    if (
        definitionbit_length is not None
        and definitionbit_length < input_operator.current_number_spins()
    ):
        raise ValueError(
            f"The number of spins in the operators passed is \
            {input_operator.current_number_spins()}. The length of the \
            DefinitionBit input is {definitionbit_length}, which is smaller. \
            The measurement can therefore not be constructed."
        )

    # TODO: take operators names
    circuits: list[QuantumCircuit] = []

    # sim = Aer.get_backend("aer_simulator")
    # circuits_transpiled = transpile(circuits_with_meas, sim)
    # result = sim.run(circuits_transpiled, shots=shots, memory=True).result()

    # expectation_values = []
    # for circ_idx in range(len(circuits)):
    #     br_tmp = {}
    #     for meas_idx in range(number_meas_circuits):
    #         bitstring_qiskit = result.get_memory(circ_idx * number_meas_circuits + meas_idx)
    #         bitsring_qoqo = bitstrings_qiskit_to_bool(bitstring_qiskit)
    #         br_tmp[f"ro_{meas_idx}"] = bitsring_qoqo
    #     expectation_values.append(meas.evaluate(br_tmp, {}, {}))
    return circuits


def _sort_spin_operator(input_operator: "PauliOperator") -> List:
    """
    Split a PauliOperator-like object into a list of PauliOperators,
    each containing only mutually measurement-compatible PauliProducts.

    Note: This is a greedy heuristic (same as the Rust code). It does NOT
    guarantee the minimum number of groups.
    """
    output_ops: List[PauliOperator] = []
    sorted_keys = _sort_by_length(input_operator)

    # Rust asserts sorted.len() == input_operator.len()
    # Here we’ll just proceed.

    while sorted_keys:
        new_op = PauliOperator()
        new_sorted = []

        first = sorted_keys.pop(0)
        new_op.set(first, input_operator.get(first))

        # Iterate over a snapshot (Rust clones sorted -> tmp_sorted)
        for pp in list(sorted_keys):
            # Check pp against all keys already in new_op
            incompatible_with_group = any(
                _pauli_products_are_not_measurement_compatible(existing_pp, pp)
                for existing_pp in new_op.keys()
            )
            if not incompatible_with_group:
                new_op.set(pp, input_operator.get(pp))
            else:
                new_sorted.append(pp)

        sorted_keys = new_sorted
        output_ops.append(new_op)

    return output_ops


def _sort_by_length(op: "PauliHamiltonian") -> List:
    """Return op.keys() ordered then reversed.

    Rust's Ord for PauliProduct is "by length then content" (effectively).
    Here we emulate with: (length, string) ascending, then reverse.
    """
    keys = op.keys()
    keys.sort(key=lambda pp: (_pp_length(pp), str(pp)))
    keys.reverse()
    return keys


def _pauli_products_are_not_measurement_compatible(pp_a: str, pp_b: str) -> bool:
    """Returns True iff the two PauliProducts are NOT measurement compatible.

    It works under the "single-qubit basis rotation then Z-measurement" model.
    Incompatible if there exists a qubit where both have non-identity Paulis
    and they differ (e.g., X vs Z).
    """
    a = _pp_to_local_map(pp_a)
    b = _pp_to_local_map(pp_b)
    for q in set(a.keys()) | set(b.keys()):
        pa = a.get(q, "I")
        pb = b.get(q, "I")
        if pa != "I" and pb != "I" and pa != pb:
            return True
    return False


def _pp_length(pp: str) -> int:
    """Number of non-identity factors (weight of the Pauli string)."""
    return len(_pp_to_local_map(pp))


def _pp_to_local_map(pp: str) -> Dict[int, str]:
    """Convert a PauliProduct into a dict {qubit_index: 'X'|'Y'|'Z'}.

    Identity on a qubit is represented by absence from the dict.
    """
    s = str(pp).strip()
    if s in ("", "I"):  # tolerate empty / identity representations
        return {}
    out: Dict[int, str] = {}
    for q_str, p in _TOKEN_RE.findall(s):
        out[int(q_str)] = p
    return out
