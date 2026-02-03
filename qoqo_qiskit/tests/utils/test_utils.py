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

import pytest
import sys

from qoqo_qiskit.utils import (
    struqture_hamiltonian_to_qiskit_op,
    measure_spin_operator_to_qiskit,
    _sort_by_length,
)
from struqture_py.spins import PauliHamiltonian, PauliProduct  # type:ignore


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

    hamiltonian_1 = PauliHamiltonian()
    hamiltonian_1.add_operator_product(pp_1, 0.5)

    hamiltonian_2 = PauliHamiltonian()
    hamiltonian_2.add_operator_product(pp_1, 0.5)
    hamiltonian_2.add_operator_product(pp_2, 0.5)

    hamiltonian_3 = PauliHamiltonian()
    hamiltonian_3.add_operator_product(pp_1, 0.5)
    hamiltonian_3.add_operator_product(pp_3, 0.5)

    hamiltonian_4 = PauliHamiltonian()
    hamiltonian_4.add_operator_product(pp_3, 0.5)
    hamiltonian_4.add_operator_product(pp_1, 0.5)

    assert _sort_by_length(hamiltonian_1) == [pp_1]
    assert _sort_by_length(hamiltonian_2) == [pp_2, pp_1]
    assert _sort_by_length(hamiltonian_3) == [pp_1, pp_3]
    assert _sort_by_length(hamiltonian_4) == [pp_1, pp_3]

# For pytest
if __name__ == "__main__":
    pytest.main(sys.argv)
