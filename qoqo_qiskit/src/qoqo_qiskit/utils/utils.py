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
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, transpile
from qiskit.circuit import Gate
from qiskit.primitives import SamplerPubResult
from qiskit.quantum_info.operators import SparsePauliOp
from qiskit_aer import Aer
from qiskit_aer.primitives import SamplerV2
from qoqo import Circuit
from qoqo.measurements import PauliZProduct, PauliZProductInput
from struqture_py.spins import PauliHamiltonian, PauliOperator, PauliProduct  # type:ignore

from qoqo_qiskit.interface import to_qiskit_circuit

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


def run_spin_operator(
    input_circuit: Circuit,
    input_operator: PauliOperator,
    name: str,
    undo_basis_rotation: bool,
    constant_circuit: Optional[Circuit] = None,
    number_measurements: Optional[int] = None,
    qubit_mapping: Optional[dict[int, int]] = None,
    creg_length: Optional[int] = None,
) -> Tuple[List[QuantumCircuit], List[float], List[Any]]:
    circuits, op_terms, op_coeffs = measure_spin_operator(
        input_operator,
        name,
        undo_basis_rotation,
        qubit_mapping,
        creg_length,
    )

    qiskit_circuit, _ = to_qiskit_circuit(input_circuit, None)
    for circuit in circuits:
        circuit.compose(qiskit_circuit, front=True, inplace=True)
        if constant_circuit:
            circuit.compose(constant_circuit, front=True)

    sampler = SamplerV2()
    shots = number_measurements if number_measurements else sampler.default_shots
    res = sampler.run(circuits, shots=shots).result()

    all_shots: list[list[str]] = []
    term_expectations: dict[Any, float] = {}
    overall_exp: complex = 0.0 + 0.0j

    for i, pub_res in enumerate(res):
        # If you have multiple classical registers, pass names=[...] here.
        ba = pub_res.join_data()  # BitArray ([docs.quantum.ibm.com](https://docs.quantum.ibm.com/api/qiskit/qiskit.primitives.SamplerPubResult?utm_source=openai))
        n_bits = ba.num_bits

        # per-shot samples (strings like "0101..."); length == shots
        shots_i = ba.get_bitstrings()
        all_shots.append(shots_i)

        # Build diagonal observables (I/Z only) for each term in this group.
        obs = [
            _z_label_from_pauli_product(k, n_bits, qubit_mapping=qubit_mapping)
            for k in op_terms[i]
        ]

        # Vector of <P_k> for this group; returns real floats for diagonal observables. ([docs.quantum.ibm.com](https://docs.quantum.ibm.com/api/qiskit/qiskit.primitives.BitArray))
        expvals = np.asarray(ba.expectation_values(obs), dtype=float)

        # Store per-term expectations
        for k, ev in zip(op_terms[i], expvals, strict=False):
            term_expectations[k] = float(ev)

        # Linear combination (this is the “linear expectation value” part)
        overall_exp += np.dot(op_coeffs[i], expvals)
    # # Get the BitArray holding the shot samples.
    # # If you have exactly one classical register, join_data() is convenient:
    # # ba = res[0].join_data()  # BitArray
    # # otherwise
    # # ba = res[0].data["meas"]  # (use your creg name)
    # ba = res[0]

    # n = ba.data.test_0.num_bits

    # single_z_ops = ["I" * i + "Z" + "I" * (n - i - 1) for i in range(n)]
    # z_expectations = ba.expectation_values(single_z_ops)
    # # sim = Aer.get_backend("aer_simulator")
    # # circuits_transpiled = transpile(circuits_with_meas, sim)
    # # result = sim.run(circuits_transpiled, shots=shots, memory=True).result()

    # # expectation_values = []
    # # for circ_idx in range(len(circuits)):
    # #     br_tmp = {}
    # #     for meas_idx in range(number_meas_circuits):
    # #         bitstring_qiskit = result.get_memory(circ_idx * number_meas_circuits + meas_idx)
    # #         bitsring_qoqo = bitstrings_qiskit_to_bool(bitstring_qiskit)
    # #         br_tmp[f"ro_{meas_idx}"] = bitsring_qoqo
    # #     expectation_values.append(meas.evaluate(br_tmp, {}, {}))
    # # return (circuits, z_expectations, ba)
    return circuits, all_shots, term_expectations, overall_exp


def measure_spin_operator(
    input_operator: PauliOperator,
    name: str,
    undo_basis_rotation: bool,
    qubit_mapping: Optional[dict[int, int]] = None,
    creg_length: Optional[int] = None,
) -> Tuple[List[QuantumCircuit], List[str], List[complex]]:
    """Create a optimized PauliZ-basis measurement circuit of all of the terms in a PauliOperator.

    Args:
        input_operator (PauliOperator): The struqture_py.spins.PauliOperator instance.
        name (str): Name for the measurement circuit.
        undo_basis_rotation (bool): Whether to append operations undoing basis rotations or not.
        qubit_mapping (Optional[dict[int, int]]): Optional qubit mapping to apply to
            the measurement circuit.
        creg_length (Optional[int]): Optional length of the ClassicalRegister instance.

    Returns:
        List[QuantumCircuit]: The list of optimized PauliZ-basis measurement circuits.
    """
    if creg_length is not None and creg_length < input_operator.current_number_spins():
        raise ValueError(
            f"The number of spins in the operators passed is \
            {input_operator.current_number_spins()}. The length of the \
            DefinitionBit input is {creg_length}, which is smaller. \
            The measurement can therefore not be constructed."
        )

    operators: List[PauliOperator] = _sort_spin_operator(input_operator)
    circuits: List[QuantumCircuit] = []
    operators_terms: List[str] = []
    operators_coeffs: List[complex] = []

    for i, pp in enumerate(operators):
        terms = pp.keys()
        coeffs = np.array([complex(pp.get(t)) for t in terms], dtype=complex)
        circuit = _single_measurement_circuit(
            pp.keys(),
            f"{name}_{i}",
            undo_basis_rotation,
            qubit_mapping,
            input_operator.current_number_spins(),
            creg_length,
        )
        circuits.append(circuit)
        operators_terms.append(terms)
        operators_coeffs.append(coeffs)

    return (circuits, operators_terms, operators_coeffs)


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
    mapping = qubit_mapping if qubit_mapping is not None else {}
    circuit = QuantumCircuit(number_qubits)
    creg_length = creg_length if creg_length is not None else number_qubits
    creg = ClassicalRegister(creg_length, readout_register)
    circuit.add_register(creg)

    _basis_rotation_from_z_basis(circuit, pauli_products, mapping)

    circuit.measure(range(number_qubits), creg)

    if undo_basis_rotation:
        _basis_rotation_to_z_basis(circuit, pauli_products, mapping)

    return circuit


def _basis_rotation_from_z_basis(
    circuit: QuantumCircuit,
    pauli_products: List[PauliProduct],
    qubit_mapping: Optional[Dict[int, int]],
) -> QuantumCircuit:
    collected_pauli_products, _ = _collect_pauli_products(pauli_products)

    mapping = qubit_mapping if qubit_mapping is not None else {}

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

    mapping = qubit_mapping if qubit_mapping is not None else {}

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
    if len(collected_pauli_products.keys()) == 0:
        max_length = 1
    else:
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


def _z_label_from_pauli_product(
    pauli_product: PauliProduct,
    n: int,
    qubit_mapping: Optional[dict[int, int]] = None,
) -> str:
    """Build a *diagonal* observable label ('I'/'Z' only) of length n.

    Assuming the circuit already rotated X/Y -> Z before measuring.
    Qiskit label convention: rightmost char = qubit 0.
    BitArray convention: bit index 0 is least-significant/rightmost. ([docs.quantum.ibm.com](https://docs.quantum.ibm.com/api/qiskit/qiskit.primitives.BitArray))
    """
    label = ["I"] * n
    mapping = qubit_mapping if qubit_mapping is not None else {}

    # This assumes your PauliProduct iterates like: for (q, op) in pauli_product
    # where op is something like "X","Y","Z" (or an enum).
    for qbt in pauli_product.keys():
        pauli_str = pauli_product.get(qbt)
        qubit = mapping[qbt] if qbt in mapping else qbt
        if pauli_str == "I":
            continue
        if not (0 <= qubit < n):
            raise ValueError(f"Mapped qubit index {qubit} out of range for n={n}")

        # Put 'Z' on measured qubit position.
        label[n - 1 - qubit] = "Z"

    return "".join(label)


# def measure_spin_operator_to_qiskit(
#     input_operator,  # your PauliOperator type: mapping PauliProduct -> complex coeff
#     name: str,
#     undo_basis_rotation: bool,
#     number_measurements: Optional[int] = None,
#     qubit_mapping: Optional[dict[int, int]] = None,
#     definitionbit_length: Optional[int] = None,
# ) -> tuple[
#     list,  # circuits
#     list[list[str]],  # shot bitstrings per commuting group circuit
#     dict[Any, float],  # per-term expectation values <P> (real floats)
#     complex,  # overall <O>
# ]:
#     n_spins = input_operator.current_number_spins()

#     if definitionbit_length is not None and definitionbit_length < n_spins:
#         raise ValueError(
#             f"The number of spins in the operators passed is {n_spins}. "
#             f"The length of the DefinitionBit input is {definitionbit_length}, which is smaller."
#         )

#     # Your grouping: list of PauliOperator, each group measurable in one circuit
#     groups = _sort_spin_operator(input_operator)

#     circuits = []
#     group_keys: list[list] = []  # list of PauliProducts per group, in a stable order
#     group_coeffs: list[np.ndarray] = []

#     for i, group_op in enumerate(groups):
#         keys = list(group_op.keys())
#         coeffs = np.array([complex(group_op[k]) for k in keys], dtype=complex)

#         circ = _single_measurement_circuit(
#             keys,
#             f"{name}_{i}",
#             undo_basis_rotation,
#             qubit_mapping,
#             n_spins,
#             definitionbit_length,
#         )
#         circuits.append(circ)
#         group_keys.append(keys)
#         group_coeffs.append(coeffs)

#     sampler = SamplerV2()
#     shots = number_measurements if number_measurements is not None else sampler.default_shots
#     prim_result = sampler.run(circuits, shots=shots).result()

#     all_shots: list[list[str]] = []
#     term_expectations: dict[Any, float] = {}
#     overall_exp: complex = 0.0 + 0.0j

#     for i, pub_res in enumerate(prim_result):
#         # If you have multiple classical registers, pass names=[...] here.
#         ba = pub_res.join_data()  # BitArray ([docs.quantum.ibm.com](https://docs.quantum.ibm.com/api/qiskit/qiskit.primitives.SamplerPubResult?utm_source=openai))
#         n_bits = ba.num_bits

#         # per-shot samples (strings like "0101..."); length == shots
#         shots_i = ba.get_bitstrings()
#         all_shots.append(shots_i)

#         # Build diagonal observables (I/Z only) for each term in this group.
#         obs = [
#             _z_label_from_pauli_product(k, n_bits, qubit_mapping=qubit_mapping)
#             for k in group_keys[i]
#         ]

#         # Vector of <P_k> for this group; returns real floats for diagonal observables. ([docs.quantum.ibm.com](https://docs.quantum.ibm.com/api/qiskit/qiskit.primitives.BitArray))
#         expvals = np.asarray(ba.expectation_values(obs), dtype=float)

#         # Store per-term expectations
#         for k, ev in zip(group_keys[i], expvals):
#             term_expectations[k] = float(ev)

#         # Linear combination (this is the “linear expectation value” part)
#         overall_exp += np.dot(group_coeffs[i], expvals)

#     return circuits, all_shots, term_expectations, overall_exp


# def measure_spin_operator_to_qiskit(
#     input_operator,
#     name: str,
#     undo_basis_rotation: bool,
#     number_measurements: Optional[int] = None,
#     qubit_mapping: Optional[dict[int, int]] = None,
#     definitionbit_length: Optional[int] = None,
# ):
#     n_spins = input_operator.current_number_spins()
#     if definitionbit_length is not None and definitionbit_length < n_spins:
#         raise ValueError("DefinitionBit length smaller than number of spins.")

#     groups = _sort_spin_operator(input_operator)  # commuting-grouping like your Rust

#     circuits = []
#     group_terms = []
#     group_coeffs = []
#     for i, group_op in enumerate(groups):
#         terms = list(group_op.keys())
#         coeffs = np.array([complex(group_op[t]) for t in terms], dtype=complex)

#         circ = _single_measurement_circuit(
#             terms, f"{name}_{i}", undo_basis_rotation, qubit_mapping, n_spins, definitionbit_length
#         )

#         circuits.append(circ)
#         group_terms.append(terms)
#         group_coeffs.append(coeffs)

#     sampler = SamplerV2()
#     shots = number_measurements if number_measurements is not None else sampler.default_shots
#     prim_result = sampler.run(circuits, shots=shots).result()

#     all_shots = []  # per-group list of bitstrings
#     term_expvals = {}  # term -> <term>
#     operator_expval = 0.0 + 0.0j  # sum coeff * <term>

#     for i, pub_res in enumerate(prim_result):
#         ba = pub_res.join_data()  # BitArray (concatenated registers) ([docs.quantum.ibm.com](https://docs.quantum.ibm.com/api/qiskit/qiskit.primitives.SamplerPubResult?utm_source=openai))

#         # raw single-shot samples:
#         all_shots.append(ba.get_bitstrings())

#         # per-term expectations for this group via internal method:
#         observables = [
#             _z_obs_label_for_term(t, ba.num_bits, qubit_mapping) for t in group_terms[i]
#         ]
#         expvals = np.asarray(
#             ba.expectation_values(observables), dtype=float
#         )  # ([docs.quantum.ibm.com](https://docs.quantum.ibm.com/api/qiskit/qiskit.primitives.BitArray?utm_source=openai))

#         for t, ev in zip(group_terms[i], expvals):
#             term_expvals[t] = float(ev)

#         operator_expval += np.dot(group_coeffs[i], expvals)

#     return circuits, all_shots, term_expvals, operator_expval
