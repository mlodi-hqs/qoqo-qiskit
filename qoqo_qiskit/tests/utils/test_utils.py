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
"""Test file for utils.py."""

import numpy as np
import pytest
import sys

from qoqo_qiskit.utils import (
    struqture_hamiltonian_to_qiskit_op,
    measure_spin_operator_to_qiskit,
    _sort_by_length,
    _sort_spin_operator,
    _single_measurement_circuit,
    _collect_pauli_products,
    _basis_rotation_from_z_basis,
)
from qiskit import QuantumCircuit
from struqture_py.spins import PauliHamiltonian, PauliProduct, PauliOperator  # type:ignore


def test_basic_hamiltonian() -> None:
    """Test struqture_hamiltonian_to_qiskit_op with a basic Hamiltonian."""
    pp = PauliProduct().x(0).z(1).y(2)

    hamiltonian = PauliHamiltonian()
    hamiltonian.add_operator_product(pp, 0.5)

    res = struqture_hamiltonian_to_qiskit_op(hamiltonian, 3)

    assert res.num_qubits == 3
    assert res.to_list() == [("YZX", (0.5 + 0j))]


def test_big_hamiltonian() -> None:
    """Test struqture_hamiltonian_to_qiskit_op with a big Hamiltonian."""
    pp = PauliProduct().x(0).z(1).y(2).x(3).z(4).y(5).x(6).z(7).y(8).x(9).z(10).y(11)
    pp2 = PauliProduct().x(12)

    hamiltonian = PauliHamiltonian()
    hamiltonian.add_operator_product(pp, 0.5)
    hamiltonian.add_operator_product(pp2, 0.25)

    res = struqture_hamiltonian_to_qiskit_op(hamiltonian, 13)

    assert res.num_qubits == 13
    assert res.to_list() == [("IYZXYZXYZXYZX", (0.5 + 0j)), ("XIIIIIIIIIIII", (0.25 + 0j))]


def test_measure_spin_operator_empty() -> None:
    """Test measure_spin_operator with an empty operator."""
    pp = PauliProduct().x(0).z(1)
    hamiltonian = PauliHamiltonian()
    hamiltonian.add_operator_product(pp, 0.5)

    with pytest.raises(ValueError) as exc:
        _ = measure_spin_operator_to_qiskit(hamiltonian, "empty", False, definitionbit_length=1)
    assert (
        "The number of spins in the operators passed is \
            2. The length of the \
            DefinitionBit input is 1, which is smaller. \
            The measurement can therefore not be constructed."
        in str(exc.value)
    )


def test_sort_by_length() -> None:
    """Test _sort_by_length function."""
    pp_1 = PauliProduct().x(0).z(1).y(4)
    pp_2 = PauliProduct().x(0).z(2).y(4)
    pp_3 = PauliProduct().x(0).y(1)

    hamiltonian = PauliOperator()

    hamiltonian_1 = PauliOperator()
    hamiltonian_1.add_operator_product(pp_1, 0.5)

    hamiltonian_2 = PauliOperator()
    hamiltonian_2.add_operator_product(pp_1, 0.5)
    hamiltonian_2.add_operator_product(pp_2, 0.5)

    hamiltonian_3 = PauliOperator()
    hamiltonian_3.add_operator_product(pp_1, 0.5)
    hamiltonian_3.add_operator_product(pp_3, 0.5)

    hamiltonian_4 = PauliOperator()
    hamiltonian_4.add_operator_product(pp_3, 0.5)
    hamiltonian_4.add_operator_product(pp_1, 0.5)

    assert _sort_by_length(hamiltonian) == []
    assert _sort_by_length(hamiltonian_1) == [pp_1]
    assert _sort_by_length(hamiltonian_2) == [pp_2, pp_1]
    assert _sort_by_length(hamiltonian_3) == [pp_1, pp_3]
    assert _sort_by_length(hamiltonian_4) == [pp_1, pp_3]


def test_sort_spin_operator() -> None:
    pp_o = PauliProduct()
    pp_1 = PauliProduct().x(0).z(1).y(4)
    pp_2 = PauliProduct().x(0).z(2).y(4)
    pp_3 = PauliProduct().x(0).y(1)
    pp_4 = PauliProduct().y(4).z(6)

    po_emp = PauliOperator()
    po_1 = PauliOperator()
    po_1.add_operator_product(pp_o, 1)
    po_2 = PauliOperator()
    po_2.add_operator_product(pp_1, 1)
    po_3 = PauliOperator()
    po_3.add_operator_product(pp_1, 1)
    po_3.add_operator_product(pp_2, 1)
    po_4 = PauliOperator()
    po_4.add_operator_product(pp_1, 1)
    po_4.add_operator_product(pp_3, 1)
    po_5 = PauliOperator()
    po_5.add_operator_product(pp_3, 1)
    po_5.add_operator_product(pp_1, 1)
    po_6 = PauliOperator()
    po_6.add_operator_product(pp_3, 1)
    po_7 = PauliOperator()
    po_7.add_operator_product(pp_1, 1)
    po_7.add_operator_product(pp_3, 1)
    po_7.add_operator_product(pp_4, 1)
    po_8 = PauliOperator()
    po_8.add_operator_product(pp_1, 1)
    po_8.add_operator_product(pp_4, 1)

    assert _sort_spin_operator(po_emp) == []
    assert _sort_spin_operator(po_1) == [po_1]
    assert _sort_spin_operator(po_2) == [po_2]
    assert _sort_spin_operator(po_3) == [po_3]
    assert _sort_spin_operator(po_4) == [po_2, po_6]
    assert _sort_spin_operator(po_5) == [po_2, po_6]
    assert _sort_spin_operator(po_7) == [po_8, po_6]


# def test_single_measurement_circuit() -> None:
#     pp = PauliProduct().x(0).z(1)
#     _single_measurement_circuit(pp, "test", False, None, 2, None)


def test_collect_pauli_products() -> None:
    pp = PauliProduct().x(0).z(1)
    pp2 = PauliProduct().x(0).z(2).y(4)
    p_err = PauliProduct().y(0)
    pp_comb = PauliProduct().x(0).z(1).z(2).y(4)

    assert (pp_comb, 5) == _collect_pauli_products([pp, pp2])

    with pytest.raises(ValueError):
        _ = _collect_pauli_products([pp, p_err])


def test_basis_rotation_from_z_basis() -> None:
    pp = PauliProduct().x(0).z(1)
    pp2 = PauliProduct().x(0).z(2).y(4)
    circuit = QuantumCircuit(5)

    _basis_rotation_from_z_basis(circuit, [pp, pp2], None)

    assert_circ = QuantumCircuit(5)
    assert_circ.ry(-np.pi / 2, 0)
    assert_circ.rx(np.pi / 2, 4)
    assert circuit == assert_circ


# For pytest
if __name__ == "__main__":
    pytest.main(sys.argv)
