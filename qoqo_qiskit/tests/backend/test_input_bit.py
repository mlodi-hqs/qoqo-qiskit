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
"""Test running local operation with qasm backend."""
from qoqo_qiskit import QoqoQiskitBackend
from qoqo import Circuit, QuantumProgram
from qoqo.measurements import ClassicalRegister, PauliZProductInput, PauliZProduct  # type:ignore
from qoqo import operations as ops  # type:ignore
import pytest
import sys

list_of_operations = [
    [ops.PauliX(1), ops.PauliX(0), ops.PauliZ(2), ops.PauliX(3), ops.PauliY(4)],
    [
        ops.Hadamard(0),
        ops.CNOT(0, 1),
        ops.CNOT(1, 2),
        ops.CNOT(2, 3),
        ops.CNOT(3, 4),
    ],
    [ops.RotateX(0, 0.23), ops.RotateY(1, 0.12), ops.RotateZ(2, 0.34)],
]


def test_running_with_input_bit() -> None:
    """Test running simple circuit with InputBit."""
    circuit = Circuit()
    circuit += ops.DefinitionBit("ro", 2, True)
    circuit += ops.InputBit("ro", 1, True)
    circuit += ops.PauliX(0)
    # circuit += ops.PragmaRepeatedMeasurement("ro", 2)
    circuit += ops.MeasureQubit(0, "ro", 0)
    circuit += ops.MeasureQubit(1, "ro", 1)
    circuit += ops.PragmaSetNumberOfMeasurements(2, "ro")

    backend = QoqoQiskitBackend()
    (bit_res, _, _) = backend.run_circuit(circuit)
    assert "ro" in bit_res.keys()
    registers = bit_res["ro"]

    assert len(registers) == 2
    assert len(registers[0]) == 2
    assert registers[0] == [True, True]

    circuit = Circuit()
    circuit += ops.DefinitionBit("ro", 3, True)
    circuit += ops.InputBit("ro", 2, True)
    circuit += ops.MeasureQubit(0, "ro", 0)
    circuit += ops.MeasureQubit(1, "ro", 1)
    circuit += ops.PragmaSetNumberOfMeasurements(2, "ro")

    backend = QoqoQiskitBackend()
    (bit_res, _, _) = backend.run_circuit(circuit)
    assert "ro" in bit_res.keys()
    registers = bit_res["ro"]

    assert len(registers) == 2
    assert len(registers[0]) == 3
    assert registers[0] == [False, False, True]
    assert registers[1] == [False, False, True]


def test_running_with_input_bit_lists() -> None:
    """Test running lists of circuits with InputBit."""
    circuit_0 = Circuit()
    circuit_0 += ops.DefinitionBit("ro", 2, True)
    circuit_0 += ops.InputBit("ro", 1, True)
    circuit_0 += ops.PauliX(0)
    circuit_0 += ops.MeasureQubit(0, "ro", 0)
    circuit_0 += ops.MeasureQubit(1, "ro", 1)
    circuit_0 += ops.PragmaSetNumberOfMeasurements(5, "ro")

    circuit_1 = Circuit()
    circuit_1 += ops.DefinitionBit("ri", 3, True)
    circuit_1 += ops.InputBit("ri", 2, True)
    circuit_1 += ops.InputBit("ri", 1, True)
    circuit_1 += ops.MeasureQubit(0, "ri", 0)
    circuit_1 += ops.MeasureQubit(1, "ri", 1)
    circuit_1 += ops.PragmaSetNumberOfMeasurements(5, "ri")

    backend = QoqoQiskitBackend()
    (bit_res, _, _) = backend.run_circuit_list([circuit_0, circuit_1])
    assert "ro" in bit_res.keys()
    assert "ri" in bit_res.keys()
    registers_ro = bit_res["ro"]
    registers_ri = bit_res["ri"]

    assert len(registers_ro) == 5
    assert len(registers_ri) == 5
    assert [len(res) == 2 for res in registers_ro]
    assert [len(res) == 3 for res in registers_ri]
    assert registers_ro[0] == [True, True]
    assert registers_ri[0] == [False, True, True]


def test_quantum_program():
    backend = QoqoQiskitBackend()

    circuit = Circuit()
    circuit += ops.DefinitionBit("ro", 2, True)
    circuit += ops.InputBit("ro", 1, True)
    circuit += ops.PauliX(0)
    circuit += ops.RotateZ(0, "angle_0")
    circuit += ops.MeasureQubit(0, "ro", 0)
    circuit += ops.MeasureQubit(1, "ro", 1)
    circuit += ops.PragmaSetNumberOfMeasurements(2, "ro")

    measurement_input = PauliZProductInput(1, False)
    z_basis_index = measurement_input.add_pauliz_product(
        "ro",
        [
            0,
        ],
    )
    measurement_input.add_linear_exp_val(
        "<H>",
        {z_basis_index: 0.2},
    )

    measurement = PauliZProduct(
        constant_circuit=None,
        circuits=[circuit],
        input=measurement_input,
    )

    program = QuantumProgram(
        measurement=measurement,
        input_parameter_names=["angle_0"],
    )

    res = backend.run_program(program=program, params_values=[[1], [2], [3]])

    assert len(res) == 3
    for el in res:
        assert float(el["<H>"])

    res = backend.run_program(program=program, params_values=[1])

    assert float(res["<H>"])

    measurement = ClassicalRegister(constant_circuit=None, circuits=[circuit])

    program = QuantumProgram(measurement=measurement, input_parameter_names=["angle_0"])

    res = backend.run_program(program=program, params_values=[[0], [1], [2]])

    assert len(res) == 3

    res = backend.run_program(program=program, params_values=[0])

    assert "ro" in res[0].keys()


if __name__ == "__main__":
    pytest.main(sys.argv)
