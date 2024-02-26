# Copyright © 2024 HQS Quantum Simulations GmbH.
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
"""Test queued_results.py file."""

import json
import sys
from typing import Dict, List, Tuple

import pytest
from qiskit.providers import Job
from qoqo import Circuit
from qoqo import operations as ops
from qoqo.measurements import ClassicalRegister  # type:ignore
from qoqo_qiskit.backend import QoqoQiskitBackend, QueuedCircuitRun, QueuedProgramRun


def _mocked_run(
    sim_type: str = "automatic",
    register_name: str = "ri",
) -> Tuple[
    Job,
    str,
    Tuple[
        Dict[str, int],
        Dict[str, List[List[bool]]],
        Dict[str, List[List[float]]],
        Dict[str, List[List[complex]]],
    ],
    Circuit,
]:
    circuit = Circuit()
    circuit += ops.Hadamard(0)
    if sim_type == "automatic":
        circuit += ops.DefinitionBit(register_name, 1, True)
        circuit += ops.PragmaRepeatedMeasurement(register_name, 1)
    elif sim_type == "density_matrix":
        circuit += ops.DefinitionComplex(register_name, 1, True)
        circuit += ops.PragmaGetDensityMatrix(register_name, None)
    elif sim_type == "statevector":
        circuit += ops.DefinitionComplex(register_name, 1, True)
        circuit += ops.PragmaGetStateVector(register_name, None)

    backend = QoqoQiskitBackend()

    (
        job,
        sim_type,
        clas_regs_sizes,
        output_bit_register_dict,
        output_float_register_dict,
        output_complex_register_dict,
    ) = backend._run_circuit(circuit)

    register_info = (
        clas_regs_sizes,
        output_bit_register_dict,
        output_float_register_dict,
        output_complex_register_dict,
    )
    return (job, sim_type, register_info, circuit)


def test_constructors() -> None:
    """Test QueuedCircuitRun and QueuedProgramRun constructors."""
    run = _mocked_run()
    qcr = QueuedCircuitRun(
        job=run[0],
        memory=True,
        sim_type=run[1],
        registers_info=run[2],
    )

    with pytest.raises(TypeError) as exc:
        _ = QueuedProgramRun(measurement="error", queued_circuits=[qcr, qcr])
    assert "Unknown measurement type." in str(exc.value)


@pytest.mark.parametrize("sim_type", ["automatic", "density_matrix", "statevector"])
def test_to_json(sim_type: str) -> None:
    """Test QueuedCircuitRun and QueuedProgramRun `.to_json()` method."""
    run = _mocked_run(sim_type)
    qcr = QueuedCircuitRun(
        job=run[0],
        memory=True,
        sim_type=run[1],
        registers_info=run[2],
    )

    measurement = ClassicalRegister(constant_circuit=None, circuits=[run[3], run[3]])
    qpr = QueuedProgramRun(
        measurement=measurement,
        queued_circuits=[qcr, qcr],
    )

    serialized_qcr = qcr.to_json()
    serialized_json_qcr = json.loads(serialized_qcr)

    serialized_qpr = qpr.to_json()
    serialized_json_qpr = json.loads(serialized_qpr)

    assert serialized_json_qcr["sim_type"] == sim_type
    assert serialized_json_qcr["memory"]
    assert serialized_json_qcr["registers_info"] == list(run[2])
    assert serialized_json_qcr["qoqo_result"] is None

    assert serialized_json_qpr["measurement_type"] == "ClassicalRegister"
    assert serialized_json_qpr["measurement"] == measurement.to_json()
    assert serialized_json_qpr["queued_circuits"] == [
        json.dumps(serialized_json_qcr),
        json.dumps(serialized_json_qcr),
    ]
    assert serialized_json_qpr["registers"] == [{}, {}, {}]


def test_from_json() -> None:
    """Test QueuedCircuitRun and QueuedProgramRun `.from_json()` method."""
    pass


def test_poll_result() -> None:
    """Test QueuedCircuitRun and QueuedProgramRun `.poll_result()` method."""
    pass


# For pytest
if __name__ == "__main__":
    pytest.main(sys.argv)
