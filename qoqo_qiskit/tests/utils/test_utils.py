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

from qoqo_qiskit.utils import struqture_hamiltonian_to_qiskit_op
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


# For pytest
if __name__ == "__main__":
    pytest.main(sys.argv)
