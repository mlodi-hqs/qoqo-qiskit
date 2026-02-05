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
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, transpile
from qiskit.circuit import Gate
from qiskit.quantum_info.operators import SparsePauliOp
from qiskit_aer import Aer
from struqture_py.spins import PauliHamiltonian, PauliOperator, PauliProduct  # type:ignore

_TOKEN_RE = re.compile(r"(\d+)([XYZ])")


def struqture_hamiltonian_to_qiskit_op(
    pauli_hamiltonian: PauliHamiltonian,
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
    input_operator: PauliHamiltonian,
    name: str,
    undo_basis_rotation: bool,
    constant_circuit: Optional[QuantumCircuit] = None,
    number_measurements: Optional[int] = None,
    qubit_mapping: Optional[dict[int, int]] = None,
    definitionbit_length: Optional[int] = None,
) -> Tuple[list[QuantumCircuit], QuantumCircuit, int]:
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

    operators: List[PauliOperator] = _sort_spin_operator(input_operator)
    circuits: list[QuantumCircuit] = []
    temp = 0

    for i, op in enumerate(operators):
        keys: List[PauliProduct] = op.keys()

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
    return (
        circuits,
        constant_circuit,
        temp,
    )


def _sort_spin_operator(input_operator: PauliOperator) -> List[PauliOperator]:
    """Split a PauliOperator-like object into measurement-compatible PauliProducts."""
    output_ops: List[PauliOperator] = []
    sorted_keys = _sort_by_length(input_operator)

    # TODO length check

    while sorted_keys:
        new_op = PauliOperator()
        new_sorted = []

        first = sorted_keys.pop(0)
        new_op.set(first, input_operator.get(first))

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


def _single_measurement_circuit(
    pauli_products: List[PauliProduct],
    readout_register: str,
    undo_basis_rotation: bool,
    qubit_mapping: Optional[Dict[int, int]],
    number_qubits: int,
    creg_length: Optional[int],
) -> QuantumCircuit:
    mapping = dict(qubit_mapping) if qubit_mapping is not None else {}
    circuit = QuantumCircuit(number_qubits)
    creg = ClassicalRegister(creg_length, readout_register)
    circuit.add_register(creg)

    _basis_rotation_from_z_basis(circuit, pauli_products, mapping)

    circuit.measure_all()
    if undo_basis_rotation:
        pass  # TODO implement basis_rotation_to_z_basis
    return circuit


def _basis_rotation_from_z_basis(
    circuit: QuantumCircuit,
    pauli_products: List[PauliProduct],
    qubit_mapping: Optional[Dict[int, int]],
) -> QuantumCircuit:
    collected_pauli_products, _ = _collect_pauli_products(pauli_products)

    mapping = dict(qubit_mapping) if qubit_mapping is not None else {}

    for qbt in collected_pauli_products.keys():
        pauli_str = collected_pauli_products.get(qbt)
        qubit = mapping[qbt] if qbt in mapping else qbt
        if pauli_str == "X":
            circuit.ry(-np.pi / 2, qubit)
        elif pauli_str == "Y":
            circuit.rx(np.pi / 2, qubit)
    return circuit


def _basis_rotation_to_z_basis(
    circuit: QuantumCircuit,
    pauli_products: List[PauliProduct],
    qubit_mapping: Optional[Dict[int, int]],
) -> QuantumCircuit:
    collected_pauli_products, _ = _collect_pauli_products(pauli_products)

    mapping = dict(qubit_mapping) if qubit_mapping is not None else {}

    for qbt in collected_pauli_products.keys():
        pauli_str = collected_pauli_products.get(qbt)
        qubit = mapping[qbt] if qbt in mapping else qbt
        if pauli_str == "X":
            circuit.ry(np.pi / 2, qubit)
        elif pauli_str == "Y":
            circuit.rx(-np.pi / 2, qubit)
    return circuit


def _collect_pauli_products(pauli_products: List[PauliProduct]) -> Tuple[PauliProduct, int]:
    for i, pp_left in enumerate(pauli_products):
        for ppright in pauli_products[i + 1 :]:
            if _pauli_products_are_not_measurement_compatible(pp_left, ppright):
                raise ValueError("Pauli products are not measurement compatible.")
    collected_pauli_products = PauliProduct()
    for pp in pauli_products:
        for key in pp.keys():
            collected_pauli_products = collected_pauli_products.set_pauli(key, pp.get(key))
    max_length = max(collected_pauli_products.keys()) + 1
    return (collected_pauli_products, max_length)


def _sort_by_length(op: PauliOperator) -> List:
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
