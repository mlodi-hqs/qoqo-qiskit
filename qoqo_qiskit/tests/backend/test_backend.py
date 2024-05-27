# Copyright © 2023 HQS Quantum Simulations GmbH.
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
"""Test backend.py file."""

import sys
import time
from typing import Any, List

import pytest
from qiskit_aer import AerSimulator
from qoqo import Circuit, QuantumProgram
from qoqo import operations as ops
from qoqo.measurements import (  # type:ignore
    ClassicalRegister,
    PauliZProduct,
    PauliZProductInput,
)
from qoqo_qiskit.backend import QoqoQiskitBackend  # type:ignore
from qoqo_qiskit.backend.post_processing import _split
from qoqo_qiskit.backend.queued_results import QueuedCircuitRun, QueuedProgramRun


def test_constructor() -> None:
    """Test QoqoQiskitBackend constructor."""
    simulator = AerSimulator()
    try:
        _ = QoqoQiskitBackend()
        _ = QoqoQiskitBackend(simulator)
        _ = QoqoQiskitBackend(simulator, memory=True)
    except Exception:
        AssertionError()

    with pytest.raises(TypeError) as exc:
        _ = QoqoQiskitBackend("wrong_name")
    assert "The input is not a valid Qiskit Backend instance." in str(exc.value)


@pytest.mark.parametrize(
    "operations",
    [
        [ops.PauliX(1), ops.PauliX(0), ops.PauliZ(2), ops.PauliX(3), ops.PauliY(4)],
        [
            ops.Hadamard(0),
            ops.CNOT(0, 1),
            ops.CNOT(1, 2),
            ops.CNOT(2, 3),
            ops.CNOT(3, 4),
        ],
        [ops.RotateX(0, 0.23), ops.RotateY(1, 0.12), ops.RotateZ(2, 0.34)],
    ],
)
def test_run_circuit_errors(operations: List[Any]) -> None:
    """Test QoqoQiskitBackend.run_circuit method errors."""
    backend = QoqoQiskitBackend()

    with pytest.raises(TypeError) as exc:
        _ = backend.run_circuit("error")
    assert "The input is not a valid Qoqo Circuit instance." in str(exc.value)

    circuit = Circuit()
    involved_qubits = set()
    for op in operations:
        involved_qubits.update(op.involved_qubits())
        circuit += op

    with pytest.raises(ValueError) as exc:
        _ = backend.run_circuit(circuit)
    assert (
        "The Circuit does not contain Measurement, PragmaGetStateVector or "
        "PragmaGetDensityMatrix operations. Simulation not possible." in str(exc.value)
    )

    circuit_1 = Circuit()
    circuit_1 += circuit
    circuit_1 += ops.DefinitionComplex("ri", len(involved_qubits), True)
    circuit_1 += ops.PragmaGetStateVector("ri", None)
    circuit_1 += ops.PragmaGetDensityMatrix("ri", None)

    with pytest.raises(ValueError) as exc:
        _ = backend.run_circuit(circuit_1)
    assert (
        "The Circuit contains both a PragmaGetStateVector and a PragmaGetDensityMatrix "
        "instruction. Simulation not possible." in str(exc.value)
    )

    circuit_2 = Circuit()
    circuit_2 += circuit
    circuit_2 += ops.DefinitionBit("ri", len(involved_qubits), True)
    for i in range(len(involved_qubits)):
        circuit_2 += ops.MeasureQubit(i, "ri", i)
    circuit_2 += ops.PragmaRepeatedMeasurement("ri", 10)

    with pytest.raises(ValueError) as exc:
        _ = backend.run_circuit(circuit_2)
    assert "Only input Circuits containing one type of measurement." in str(exc.value)

    circuit_3 = Circuit()
    circuit_3 += circuit
    circuit_3 += ops.DefinitionBit("ri", len(involved_qubits), True)
    circuit_3 += ops.PragmaRepeatedMeasurement("ri", 10)

    try:
        _ = backend.run_circuit(circuit_3)
    except Exception:
        assert AssertionError("Correct Circuit failed on '.run_circuit()' call.")


@pytest.mark.parametrize(
    "operations",
    [
        [ops.PauliX(1), ops.PauliX(0), ops.PauliZ(2), ops.PauliX(3), ops.PauliY(4)],
        [
            ops.Hadamard(0),
            ops.CNOT(0, 1),
            ops.CNOT(1, 2),
            ops.CNOT(2, 3),
            ops.CNOT(3, 4),
        ],
        [ops.RotateX(0, 0.23), ops.RotateY(1, 0.12), ops.RotateZ(2, 0.34)],
    ],
)
def test_run_circuit_list_errors(operations: List[Any]) -> None:
    """Test QoqoQiskitBackend.run_circuit_list method errors."""
    backend = QoqoQiskitBackend()

    circuit = Circuit()
    involved_qubits = set()
    for op in operations:
        involved_qubits.update(op.involved_qubits())
        circuit += op

    with pytest.raises(TypeError) as exc:
        _ = backend.run_circuit_list("error")
    assert "The input is not a valid list of Qoqo Circuit instances." in str(exc.value)

    with pytest.raises(ValueError) as exc:
        _ = backend.run_circuit_list([])
    assert "The input is an empty list of Qoqo Circuit instances." in str(exc.value)

    circuit_0 = Circuit()
    circuit_0 += circuit
    circuit_0 += ops.DefinitionComplex("ri", 2 ** len(involved_qubits), True)
    circuit_0 += ops.PragmaGetStateVector("ri", None)

    circuit_1 = Circuit()
    circuit_1 += circuit
    circuit_1 += ops.DefinitionComplex("ri", 4 ** len(involved_qubits), True)
    circuit_1 += ops.PragmaGetDensityMatrix("ri", None)

    with pytest.raises(ValueError) as exc:
        _ = backend.run_circuit_list([circuit_0, circuit_1])
    assert "The input is a list of Qoqo Circuits with different simulation types." in str(
        exc.value
    )

    circuit_2 = Circuit()
    circuit_2 += circuit
    circuit_2 += ops.DefinitionBit("ri", len(involved_qubits), True)
    circuit_2 += ops.PragmaRepeatedMeasurement("ri", 150)

    circuit_3 = Circuit()
    circuit_3 += circuit
    circuit_3 += ops.DefinitionBit("ri", len(involved_qubits), True)
    circuit_3 += ops.PragmaRepeatedMeasurement("ri", 200)

    with pytest.raises(ValueError) as exc:
        _ = backend.run_circuit_list([circuit_2, circuit_3])
    assert "The input is a list of Qoqo Circuits with different number of shots." in str(exc.value)


@pytest.mark.parametrize(
    "operations",
    [
        [ops.PauliX(1), ops.PauliX(0), ops.PauliZ(2), ops.PauliX(3), ops.PauliY(4)],
        [
            ops.Hadamard(0),
            ops.CNOT(0, 1),
            ops.CNOT(1, 2),
            ops.CNOT(2, 3),
            ops.CNOT(3, 4),
        ],
        [ops.RotateX(0, 0.23), ops.RotateY(1, 0.12), ops.RotateZ(2, 0.34)],
    ],
)
def test_run_circuit_results(operations: List[Any]) -> None:
    """Test QoqoQiskitBackend.run_circuit method results."""
    backend = QoqoQiskitBackend()

    circuit = Circuit()
    involved_qubits = set()
    for op in operations:
        involved_qubits.update(op.involved_qubits())
        circuit += op

    circuit_1 = Circuit()
    circuit_1 += circuit
    circuit_1 += ops.DefinitionBit("ri", len(involved_qubits), True)
    circuit_1 += ops.PragmaRepeatedMeasurement("ri", 10)

    result = backend.run_circuit(circuit_1)

    assert result[0]
    assert result[0]["ri"]
    assert not result[1]
    assert not result[2]

    circuit_2 = Circuit()
    circuit_2 += circuit
    circuit_2 += ops.DefinitionComplex("ri", len(involved_qubits), True)
    circuit_2 += ops.PragmaGetStateVector("ri", None)

    result = backend.run_circuit(circuit_2)

    assert not result[0]
    assert not result[1]
    assert result[2]
    assert result[2]["ri"]
    assert len(result[2]["ri"][0]) == 2 ** len(involved_qubits)

    circuit_3 = Circuit()
    circuit_3 += circuit
    circuit_3 += ops.DefinitionComplex("ri", len(involved_qubits), True)
    circuit_3 += ops.PragmaGetDensityMatrix("ri", None)

    result = backend.run_circuit(circuit_3)

    assert not result[0]
    assert not result[1]
    assert result[2]
    assert result[2]["ri"]
    assert len(result[2]["ri"][0]) == (2 ** len(involved_qubits)) ** 2


@pytest.mark.parametrize(
    "operations",
    [
        [ops.PauliX(1), ops.PauliX(0), ops.PauliZ(2), ops.PauliX(3), ops.PauliY(4)],
        [
            ops.Hadamard(0),
            ops.CNOT(0, 1),
            ops.CNOT(1, 2),
            ops.CNOT(2, 3),
            ops.CNOT(3, 4),
        ],
        [ops.RotateX(0, 0.23), ops.RotateY(1, 0.12), ops.RotateZ(2, 0.34)],
    ],
)
def test_run_circuit_list_results(operations: List[Any]) -> None:
    """Test QoqoQiskitBackend.run_circuit_list method results."""
    backend = QoqoQiskitBackend()

    circuit = Circuit()
    involved_qubits = set()
    for op in operations:
        involved_qubits.update(op.involved_qubits())
        circuit += op

    circuit_0 = Circuit()
    circuit_0 += circuit
    circuit_0 += ops.DefinitionBit("ri", len(involved_qubits), True)
    for i in involved_qubits:
        circuit_0 += ops.MeasureQubit(i, "ri", i)

    circuit_1 = Circuit()
    circuit_1 += circuit
    circuit_1 += ops.DefinitionBit("ro", len(involved_qubits), True)
    for i in involved_qubits:
        circuit_1 += ops.MeasureQubit(i, "ro", i)

    result = backend.run_circuit_list([circuit_0, circuit_1])

    assert result[0]
    assert result[0]["ri"]
    assert result[0]["ro"]
    assert len(result[0]["ri"]) == 200
    assert len(result[0]["ro"]) == 200
    assert not result[1]
    assert not result[2]

    circuit_2 = Circuit()
    circuit_2 += circuit
    circuit_2 += ops.DefinitionComplex("ri", 2 ** len(involved_qubits), True)
    circuit_2 += ops.PragmaGetStateVector("ri", None)

    circuit_3 = Circuit()
    circuit_3 += circuit
    circuit_3 += ops.Hadamard(0)
    circuit_3 += ops.DefinitionComplex("ro", 2 ** len(involved_qubits), True)
    circuit_3 += ops.PragmaGetStateVector("ro", None)

    result = backend.run_circuit_list([circuit_2, circuit_3])

    assert not result[0]
    assert not result[1]
    assert result[2]
    assert result[2]["ri"]
    assert result[2]["ro"]
    assert len(result[2]["ri"][0]) == 2 ** len(involved_qubits)
    assert len(result[2]["ro"][0]) == 2 ** len(involved_qubits)

    circuit_4 = Circuit()
    circuit_4 += circuit
    circuit_4 += ops.DefinitionComplex("ri", 4 ** len(involved_qubits), True)
    circuit_4 += ops.PragmaGetDensityMatrix("ri", None)

    circuit_5 = Circuit()
    circuit_5 += circuit
    circuit_5 += ops.Hadamard(0)
    circuit_5 += ops.DefinitionComplex("ro", 4 ** len(involved_qubits), True)
    circuit_5 += ops.PragmaGetDensityMatrix("ro", None)

    result = backend.run_circuit_list([circuit_4, circuit_5])

    assert not result[0]
    assert not result[1]
    assert result[2]
    assert result[2]["ri"]
    assert result[2]["ro"]
    assert len(result[2]["ri"][0]) == 4 ** len(involved_qubits)
    assert len(result[2]["ro"][0]) == 4 ** len(involved_qubits)

    circuit_6 = Circuit()
    circuit_6 += circuit
    circuit_6 += ops.DefinitionBit("ro", len(involved_qubits), True)
    for i in involved_qubits:
        circuit_6 += ops.MeasureQubit(i, "ro", i)

    circuit_7 = Circuit()
    circuit_7 += circuit
    circuit_7 += ops.DefinitionBit("ro", len(involved_qubits), True)
    for i in involved_qubits:
        circuit_7 += ops.MeasureQubit(i, "ro", i)

    result = backend.run_circuit_list([circuit_6, circuit_7])

    assert result[0]
    assert result[0]["ro"]
    assert len(result[0]["ro"]) == 400
    assert not result[1]
    assert not result[2]


@pytest.mark.parametrize(
    "operations",
    [
        [ops.PauliX(1), ops.PauliX(0), ops.PauliZ(2), ops.PauliX(3), ops.PauliY(4)],
        [
            ops.Hadamard(0),
            ops.CNOT(0, 1),
            ops.CNOT(1, 2),
            ops.CNOT(2, 3),
            ops.CNOT(3, 4),
        ],
        [ops.RotateX(0, 0.23), ops.RotateY(1, 0.12), ops.RotateZ(2, 0.34)],
    ],
)
def test_measurement_register_classicalregister(operations: List[Any]) -> None:
    """Test QoqoQiskitBackend.run_measurement_registers method classical registers."""
    backend = QoqoQiskitBackend()

    circuit = Circuit()
    involved_qubits = set()
    for op in operations:
        involved_qubits.update(op.involved_qubits())
        circuit += op

    circuit += ops.DefinitionBit("ri", len(involved_qubits), True)
    circuit += ops.PragmaRepeatedMeasurement("ri", 10)

    measurement = ClassicalRegister(constant_circuit=None, circuits=[circuit])

    try:
        output = backend.run_measurement_registers(measurement=measurement)
    except Exception:
        AssertionError()

    assert output[0]["ri"]
    assert len(output[0]["ri"][0]) == len(involved_qubits)
    assert not output[1]
    assert not output[2]


@pytest.mark.parametrize(
    "operations",
    [
        [ops.PauliX(1), ops.PauliX(0), ops.PauliZ(2), ops.PauliX(3), ops.PauliY(4)],
        [
            ops.Hadamard(0),
            ops.CNOT(0, 1),
            ops.CNOT(1, 2),
            ops.CNOT(2, 3),
            ops.CNOT(3, 4),
        ],
        [ops.RotateX(0, 0.23), ops.RotateY(1, 0.12), ops.RotateZ(2, 0.34)],
    ],
)
def test_measurement(operations: List[Any]) -> None:
    """Test QoqoQiskitBackend.run_measurement method."""
    backend = QoqoQiskitBackend()

    circuit = Circuit()
    involved_qubits = set()
    for op in operations:
        involved_qubits.update(op.involved_qubits())
        circuit += op

    circuit += ops.DefinitionBit("ri", len(involved_qubits), True)
    circuit += ops.PragmaRepeatedMeasurement("ri", 10)

    pzpinput = PauliZProductInput(number_qubits=len(involved_qubits), use_flipped_measurement=True)

    measurement = PauliZProduct(constant_circuit=None, circuits=[circuit], input=pzpinput)

    try:
        _ = backend.run_measurement(measurement=measurement)
    except Exception:
        AssertionError()


def test_run_options() -> None:
    """Test QoqoQiskitBackend.run_circuit method with modified run option."""
    backend = QoqoQiskitBackend()

    circuit = Circuit()
    circuit += ops.Hadamard(0)
    circuit += ops.CNOT(0, 1)

    circuit_0 = Circuit()
    circuit_0 += circuit
    circuit_0 += ops.DefinitionBit("ri", 2, True)
    circuit_0 += ops.PragmaRepeatedMeasurement("ri", 1000)

    result = backend.run_circuit(circuit_0)

    assert len(result[0]["ri"]) == 1000

    circuit_1 = Circuit()
    circuit_1 += circuit
    circuit_1 += ops.DefinitionBit("ro", 2, True)
    circuit_1 += ops.MeasureQubit(0, "ro", 0)
    circuit_1 += ops.MeasureQubit(1, "ro", 1)
    circuit_1 += ops.PragmaSetNumberOfMeasurements(250, "ro")

    result = backend.run_circuit(circuit_1)

    assert len(result[0]["ro"]) == 250


def test_debugged_circuit() -> None:
    """Test QoqoQiskitBackend.run_circuit method with repeated Definition operations."""
    backend = QoqoQiskitBackend()

    circuit = Circuit()
    circuit += ops.DefinitionBit("ri", 1, True)
    circuit += ops.DefinitionBit("ri", 1, True)
    circuit += ops.DefinitionBit("ro", 1, True)
    circuit += ops.MeasureQubit(0, "ri", 0)
    circuit += ops.MeasureQubit(1, "ro", 0)

    circuit_test = Circuit()
    circuit_test += ops.DefinitionBit("ri", 1, True)
    circuit_test += ops.DefinitionBit("ro", 1, True)
    circuit_test += ops.MeasureQubit(0, "ri", 0)
    circuit_test += ops.MeasureQubit(1, "ro", 0)

    result = backend.run_circuit(circuit)
    comparison = backend.run_circuit(circuit_test)

    assert result == comparison


@pytest.mark.parametrize(
    "operations, outcome",
    [
        (
            [
                ops.PauliX(0),
                ops.CNOT(0, 1),
                ops.PauliX(2),
                ops.CNOT(0, 1),
                ops.PauliX(3),
            ],
            [True, False, True, True],
        ),
        (
            [
                ops.PauliX(0),
                ops.CNOT(0, 1),
                ops.CNOT(1, 2),
                ops.CNOT(2, 3),
                ops.PauliX(0),
                ops.PauliX(2),
            ],
            [False, True, False, True],
        ),
        (
            [ops.PauliX(0), ops.PauliX(2), ops.PauliX(2), ops.CNOT(0, 1)],
            [True, True, False],
        ),
    ],
)
def test_deterministic_circuit(operations: List[Any], outcome: List[bool]) -> None:
    """Test QoqoQiskitBackend deterministc circuit."""
    backend = QoqoQiskitBackend()

    circuit = Circuit()
    involved_qubits = set()
    for op in operations:
        involved_qubits.update(op.involved_qubits())
        circuit += op
    circuit += ops.DefinitionBit("ro", len(involved_qubits), True)
    circuit += ops.PragmaRepeatedMeasurement("ro", 10)

    result = backend.run_circuit(circuit)

    for el in result[0]["ro"]:
        assert el == outcome


def test_memory() -> None:
    """Test QoqoQiskitBackend memory parameter."""
    backend_no_mem = QoqoQiskitBackend(memory=False)
    backend_mem = QoqoQiskitBackend(memory=True)

    circuit = Circuit()
    circuit += ops.PauliX(0)
    circuit += ops.PauliX(2)

    circuit += ops.DefinitionBit("ro", 2, True)
    circuit += ops.DefinitionBit("ri", 1, True)
    circuit += ops.MeasureQubit(0, "ro", 0)
    circuit += ops.MeasureQubit(1, "ro", 1)
    circuit += ops.MeasureQubit(2, "ri", 0)

    result_no_mem = backend_no_mem.run_circuit(circuit)
    result_mem = backend_mem.run_circuit(circuit)

    for el1, el2 in zip(result_no_mem, result_mem):
        assert el1 == el2


def test_split() -> None:
    """Test post_processing._split method."""
    clas_regs = {}
    clas_regs["ro"] = 1
    clas_regs["ri"] = 2
    shot_result_ws = "01 1"
    shot_result_no_ws = "011"

    assert _split(shot_result_ws, clas_regs) == _split(shot_result_no_ws, clas_regs)


def test_overwrite() -> None:
    """Tests overwriting registers."""
    backend = QoqoQiskitBackend()

    circuit_1 = Circuit()
    circuit_1 += ops.DefinitionBit("same", 1, True)
    circuit_1 += ops.PauliX(0)
    circuit_1 += ops.MeasureQubit(0, "same", 0)
    circuit_1 += ops.PragmaSetNumberOfMeasurements(2, "same")

    circuit_2 = Circuit()
    circuit_2 += ops.DefinitionBit("same", 1, True)
    circuit_2 += ops.PauliX(0)
    circuit_2 += ops.PauliX(0)
    circuit_2 += ops.MeasureQubit(0, "same", 0)
    circuit_2 += ops.PragmaSetNumberOfMeasurements(2, "same")

    measurement = ClassicalRegister(constant_circuit=None, circuits=[circuit_1, circuit_2])

    try:
        output = backend.run_measurement_registers(measurement=measurement)
    except Exception:
        assert False

    # output should look like ({'same': [[True], [True], [False], [False]]}, {}, {})
    assert len(output[0]["same"]) == 4
    assert output[0]["same"][0][0]
    assert output[0]["same"][1][0]
    assert not output[0]["same"][2][0]
    assert not output[0]["same"][3][0]
    assert not output[1]
    assert not output[2]


def test_run_program() -> None:
    """Test QoqoQiskitBackend.run_program method."""
    backend = QoqoQiskitBackend()

    init_circuit = Circuit()
    init_circuit += ops.RotateX(0, "angle_0")
    init_circuit += ops.RotateY(0, "angle_1")

    z_circuit = Circuit()
    z_circuit += ops.DefinitionBit("ro_z", 1, is_output=True)
    z_circuit += ops.PragmaRepeatedMeasurement("ro_z", 1000, None)

    x_circuit = Circuit()
    x_circuit += ops.DefinitionBit("ro_x", 1, is_output=True)
    x_circuit += ops.Hadamard(0)
    x_circuit += ops.PragmaRepeatedMeasurement("ro_x", 1000, None)

    measurement_input = PauliZProductInput(1, False)
    z_basis_index = measurement_input.add_pauliz_product(
        "ro_z",
        [
            0,
        ],
    )
    x_basis_index = measurement_input.add_pauliz_product(
        "ro_x",
        [
            0,
        ],
    )
    measurement_input.add_linear_exp_val(
        "<H>",
        {x_basis_index: 0.1, z_basis_index: 0.2},
    )

    measurement = PauliZProduct(
        constant_circuit=init_circuit,
        circuits=[z_circuit, x_circuit],
        input=measurement_input,
    )

    program = QuantumProgram(
        measurement=measurement,
        input_parameter_names=["angle_0", "angle_1"],
    )

    res = backend.run_program(
        program=program, params_values=[[0.785, 0.238], [0.234, 0.653], [0.875, 0.612]]
    )

    assert len(res) == 3
    for el in res:
        assert float(el["<H>"])

    init_circuit += ops.DefinitionBit("ro", 1, True)
    init_circuit += ops.PragmaRepeatedMeasurement("ro", 1000, None)

    measurement = ClassicalRegister(constant_circuit=None, circuits=[init_circuit, init_circuit])

    program = QuantumProgram(measurement=measurement, input_parameter_names=["angle_0", "angle_1"])

    res = backend.run_program(
        program=program, params_values=[[0.785, 0.238], [0.234, 0.653], [0.875, 0.612]]
    )

    assert len(res) == 3
    assert res[0][0]
    assert not res[0][1]
    assert not res[0][2]


@pytest.mark.parametrize("memory", [True, False])
def test_run_circuit_queued(memory: bool) -> None:
    """Test QoqoQiskitBackend.run_circuit_queued method."""
    backend = QoqoQiskitBackend(memory=memory)

    circuit = Circuit()
    circuit += ops.Hadamard(0)
    circuit += ops.Hadamard(1)
    circuit += ops.DefinitionBit("ro", 2, True)
    circuit += ops.PragmaRepeatedMeasurement("ro", 50)

    qcr: QueuedCircuitRun = backend.run_circuit_queued(circuit)

    assert qcr._memory == memory
    assert qcr._sim_type == "automatic"
    assert "ro" in qcr._registers_info[0]
    assert "ro" in qcr._registers_info[1]


@pytest.mark.parametrize("memory", [True, False])
def test_run_circuit_list_queued(memory: bool) -> None:
    """Test QoqoQiskitBackend.run_circuit_list_queued method."""
    backend = QoqoQiskitBackend(memory=memory)

    circuit_0 = Circuit()
    circuit_0 += ops.Hadamard(0)
    circuit_0 += ops.Hadamard(1)
    circuit_0 += ops.DefinitionBit("ro", 2, True)
    circuit_0 += ops.PragmaRepeatedMeasurement("ro", 50)

    circuit_1 = Circuit()
    circuit_1 += ops.Hadamard(0)
    circuit_1 += ops.Hadamard(1)
    circuit_1 += ops.PauliX(1)
    circuit_1 += ops.DefinitionBit("ri", 2, True)
    circuit_1 += ops.PragmaRepeatedMeasurement("ri", 50)

    qcrs = backend.run_circuit_list_queued([circuit_0, circuit_1])

    assert qcrs[0]._job == qcrs[1]._job
    assert qcrs[0]._memory == qcrs[1]._memory == memory
    assert qcrs[0]._sim_type == qcrs[1]._sim_type == "automatic"
    assert "ro" in qcrs[0]._registers_info[0]
    assert "ro" in qcrs[0]._registers_info[1]
    assert "ri" in qcrs[1]._registers_info[0]
    assert "ri" in qcrs[1]._registers_info[1]

    time.sleep(1)

    poll1 = qcrs[0].poll_result()
    poll2 = qcrs[1].poll_result()

    assert len(poll1[0]["ro"]) == 50
    assert len(poll2[0]["ri"]) == 50


@pytest.mark.parametrize("memory", [True, False])
def test_run_measurement_queued(memory: bool) -> None:
    """Test QoqoQiskitBackend.run_measurement_queued method."""
    backend = QoqoQiskitBackend(memory=memory)

    circuit_0 = Circuit()
    circuit_0 += ops.Hadamard(0)
    circuit_0 += ops.Hadamard(1)
    circuit_0 += ops.DefinitionBit("ro", 2, True)
    circuit_0 += ops.PragmaRepeatedMeasurement("ro", 50)
    circuit_1 = Circuit()
    circuit_1 += ops.Hadamard(0)
    circuit_1 += ops.Hadamard(1)
    circuit_1 += ops.DefinitionBit("ri", 2, True)
    circuit_1 += ops.PragmaRepeatedMeasurement("ri", 50)

    measurement = ClassicalRegister(constant_circuit=None, circuits=[circuit_0, circuit_1])

    qpr: QueuedProgramRun = backend.run_measurement_queued(measurement=measurement)

    assert qpr._measurement == measurement
    assert len(qpr._queued_circuits) == 2


def test_run_program_queued() -> None:
    """Test QoqoQiskitBackend.run_program_queued method."""
    backend = QoqoQiskitBackend()

    init_circuit = Circuit()
    init_circuit += ops.RotateX(0, "angle_0")
    init_circuit += ops.RotateY(0, "angle_1")

    z_circuit = Circuit()
    z_circuit += ops.DefinitionBit("ro_z", 1, is_output=True)
    z_circuit += ops.PragmaRepeatedMeasurement("ro_z", 1000, None)

    x_circuit = Circuit()
    x_circuit += ops.DefinitionBit("ro_x", 1, is_output=True)
    x_circuit += ops.Hadamard(0)
    x_circuit += ops.PragmaRepeatedMeasurement("ro_x", 1000, None)

    measurement_input = PauliZProductInput(1, False)
    z_basis_index = measurement_input.add_pauliz_product(
        "ro_z",
        [
            0,
        ],
    )
    x_basis_index = measurement_input.add_pauliz_product(
        "ro_x",
        [
            0,
        ],
    )
    measurement_input.add_linear_exp_val(
        "<H>",
        {x_basis_index: 0.1, z_basis_index: 0.2},
    )

    measurement = PauliZProduct(
        constant_circuit=init_circuit,
        circuits=[z_circuit, x_circuit],
        input=measurement_input,
    )

    program = QuantumProgram(measurement=measurement, input_parameter_names=["angle_0", "angle_1"])

    with pytest.raises(ValueError) as exc:
        _ = backend.run_program_queued(program=program, params_values=[[0.4]])
    assert "Wrong number of parameters 2 parameters expected 1 parameters given." in str(exc.value)

    with pytest.raises(ValueError) as exc:
        _ = backend.run_program_queued(program=program, params_values=[])
    assert (
        "Wrong parameters value: no parameters values provided but input QuantumProgram has 2 input parameter names."
        in str(exc.value)
    )

    queued_jobs = backend.run_program_queued(
        program=program, params_values=[[0.785, 0.238], [0.234, 0.653], [0.875, 0.612]]
    )

    assert len(queued_jobs) == 3

    for queued in queued_jobs:
        while queued.poll_result() is None:
            time.sleep(1)

        serialised = queued.to_json()
        with pytest.raises(ValueError) as exc:
            _ = QueuedProgramRun.from_json(serialised)
        assert "Retrieval is not possible." in str(exc.value)


# For pytest
if __name__ == "__main__":
    pytest.main(sys.argv)
