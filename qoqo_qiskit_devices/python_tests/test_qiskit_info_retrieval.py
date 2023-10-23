"""Test qoqo_qiskit_devices information retrieval"""
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

import pytest
import sys
import numpy as np
import warnings

from qoqo_qiskit_devices import (
    ibm_devices,
    set_qiskit_noise_information,
    get_error_on_gate_model,
)


def test_info_update():
    """Test set_qiskit_noise_information method."""
    belem = ibm_devices.IBMBelemDevice()

    assert belem.single_qubit_gate_time("PauliX", 0) == 1.0
    assert belem.two_qubit_gate_time("CNOT", 0, 1) == 1.0
    assert belem.three_qubit_gate_time("ControlledControlledPauliZ", 0, 1, 2) == None
    assert belem.multi_qubit_gate_time("MultiQubitMS", [0, 1, 2, 3]) == None
    assert np.all(belem.qubit_decoherence_rates(0) == 0.0)

    with warnings.catch_warnings(record=True) as w:
        set_qiskit_noise_information(belem, get_mocked_information=True)

        assert len(w) == 1
        assert issubclass(w[-1].category, UserWarning)
        assert "dephasing" in str(w[-1].message)
        assert belem.single_qubit_gate_time("PauliX", 0) != 1.0
        assert belem.two_qubit_gate_time("CNOT", 0, 1) != 1.0
        assert (
            belem.three_qubit_gate_time("ControlledControlledPauliZ", 0, 1, 2) == None
        )
        assert belem.multi_qubit_gate_time("MultiQubitMS", [0, 1, 2, 3]) == None
        assert np.any(belem.qubit_decoherence_rates(0) != 0.0)


def test_noise_model():
    """Test get_error_on_gate_model method."""
    perth = ibm_devices.IBMPerthDevice()

    with warnings.catch_warnings(record=True) as w:
        noise_model = get_error_on_gate_model(perth, get_mocked_information=True)

        assert len(w) == 1
        assert issubclass(w[-1].category, UserWarning)
        assert "dephasing" in str(w[-1].message)

        for gate in [
            gate for gate in perth.single_qubit_gate_names() if gate != "RotateZ"
        ]:
            for qubit in range(0, perth.number_qubits()):
                assert noise_model.get_single_qubit_gate_error(gate, qubit) is not None

        for gate in perth.two_qubit_gate_names():
            for edge in perth.two_qubit_edges():
                assert (
                    noise_model.get_two_qubit_gate_error(gate, edge[0], edge[1])
                    is not None
                )


if __name__ == "__main__":
    pytest.main(sys.argv)
