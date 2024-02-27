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
"""Helper to use qiskit transpiler for qoqo circuits."""

import re
from numpy import pi
from qoqo_qasm import QasmBackend, qasm_str_to_circuit
from qoqo import Circuit, QuantumProgram
from qoqo.measurements import (
    PauliZProduct,
    ClassicalRegister,
    CheatedPauliZProduct,
    Cheated,
)
from qiskit import QuantumCircuit, transpile
from qiskit.qasm2 import dumps


def replace_math_expressions(input_string: str) -> str:
    """Replace all math expressions in the given string with their values.

    Args:
        input_string (str): String to replace math expressions in.

    Returns:
        str: String with all math expressions replaced.
    """

    def repl(match: re.Match) -> str:
        """Replace the given math expression by its value.

        Args:
            match (re.Match): the match to replace: n * pi|m / k, all optional

        Returns:
            str: the value of the given expression.
        """
        if match.group(2) is None and match.group(5) is None:
            return str(match.group(0))
        left_number = float(match.group(2)) if match.group(2) is not None else 1.0
        middle_number = 1
        if match.group(3) is not None:
            middle_number = float(match.group(3)) if match.group(3) != "pi" else pi
        right_number = float(match.group(5)) if match.group(5) is not None else 1.0
        return str(round(left_number * middle_number / right_number, 12))[:-1]

    pat = r"(([\d.]+)?\*)?(pi|[\d.]+)(\/?([\d.]+))?"
    return re.sub(pat, repl, input_string)


def transpile_with_qiskit(
    circuits: Circuit | list[Circuit], transpilers: list[dict[str, str]]
) -> Circuit:
    """Use qiskit transpilers to transpile a qoqo circuit.

    Args:
        circuits (Circuit | List[Circuits]): qoqo circuit(s) to transpile.
        transpilers (list[dict[str, str]]): transpilers to use.

    Returns:
        Circuit: transpiled qoqo circuit.
    """
    circuits_is_list = isinstance(circuits, list)
    circuits = circuits if circuits_is_list else [circuits]

    qasm_backend = QasmBackend(qasm_version="2.0")
    qiskit_circuits = [
        QuantumCircuit.from_qasm_str(qasm_backend.circuit_to_qasm_str(circuit))
        for circuit in circuits
    ]
    for transpiler_args in transpilers:
        qiskit_circuits = transpile(
            qiskit_circuits,
            backend=transpiler_args.get("backend"),
            basis_gates=transpiler_args.get("basis_gates"),
            inst_map=transpiler_args.get("inst_map"),
            coupling_map=transpiler_args.get("coupling_map"),
            backend_properties=transpiler_args.get("backend_properties"),
            initial_layout=transpiler_args.get("initial_layout"),
            layout_method=transpiler_args.get("layout_method"),
            routing_method=transpiler_args.get("routing_method"),
            translation_method=transpiler_args.get("translation_method"),
            scheduling_method=transpiler_args.get("scheduling_method"),
            instruction_durations=transpiler_args.get("instruction_durations"),
            dt=transpiler_args.get("dt"),
            approximation_degree=transpiler_args.get("approximation_degree") or 1.0,
            timing_constraints=transpiler_args.get("timing_constraints"),
            seed_transpiler=transpiler_args.get("seed_transpiler"),
            optimization_level=transpiler_args.get("optimization_level"),
            callback=transpiler_args.get("callback"),
            output_name=transpiler_args.get("output_name"),
            unitary_synthesis_method=transpiler_args.get("unitary_synthesis_method") or "default",
            target=transpiler_args.get("target"),
            hls_config=transpiler_args.get("hls_config"),
            init_method=transpiler_args.get("init_method"),
            optimization_method=transpiler_args.get("optimization_method"),
            ignore_backend_supplied_default_methods=transpiler_args.get(
                "ignore_backend_supplied_default_methods"
            )
            or False,
        )

    def qiskit_to_qoqo_circuit(qiskit_circuit: QuantumCircuit) -> Circuit:
        """Convert a qiskit circuit to a qoqo circuit.

        Args:
            qiskit_circuit (QuantumCircuit): qiskit circuit to convert.

        Returns:
            Circuit: converted qoqo circuit.
        """
        print(qiskit_circuit)
        qiskit_qasm_circuit = dumps(qiskit_circuit)
        qiskit_qasm_circuit = replace_math_expressions(qiskit_qasm_circuit)
        qiskit_qasm_circuit += "\n"
        return qasm_str_to_circuit(qiskit_qasm_circuit)

    transpiled_qoqo_circuits = [
        qiskit_to_qoqo_circuit(transpiled_qiskit_circuit)
        for transpiled_qiskit_circuit in qiskit_circuits
    ]
    return transpiled_qoqo_circuits if circuits_is_list else transpiled_qoqo_circuits[0]


def transpile_program_with_qiskit(
    quantum_program: QuantumProgram, transpilers: list[dict[str, str]]
) -> QuantumProgram:
    """Use qiskit transpilers to transpile a QuantumProgram.

    Args:
        quantum_program (QuantumProgram): QuantumProgram to transpile.
        transpilers (list[dict[str, str]]): transpilers to use.

    Returns:
        QuantumProgram: transpiled QuantumProgram.
    """
    constant_circuit = quantum_program.measurement().constant_circuit()
    circuits = quantum_program.measurement().circuits()
    circuits = (
        circuits
        if constant_circuit is None
        else [constant_circuit + circuit for circuit in circuits]
    )
    transpiled_circuits = transpile_with_qiskit(circuits, transpilers)

    def recreate_measurement(
        quantum_program: QuantumProgram, transpiled_circuits: list[Circuit]
    ) -> PauliZProduct | ClassicalRegister | CheatedPauliZProduct | Cheated:
        """Recreate a measurement QuantumProgram using the transpiled circuits.

        Args:
            quantum_program (QuantumProgram): quantumProgram to transpile.
            transpiled_circuits (list[Circuit]): transpiled circuits.

        Returns:
            Measurement: measurement

        Raises:
            TypeError: if the measurement type is not supported.
        """
        if isinstance(quantum_program.measurement(), PauliZProduct):
            return PauliZProduct(
                constant_circuit=None,
                circuits=transpiled_circuits,
                input=quantum_program.measurement().input(),
            )
        elif isinstance(quantum_program.measurement(), CheatedPauliZProduct):
            return CheatedPauliZProduct(
                constant_circuit=None,
                circuits=transpiled_circuits,
                input=quantum_program.measurement().input(),
            )
        elif isinstance(quantum_program.measurement(), Cheated):
            return Cheated(
                constant_circuit=None,
                circuits=transpiled_circuits,
                input=quantum_program.measurement().input(),
            )
        elif isinstance(quantum_program.measurement(), ClassicalRegister):
            return ClassicalRegister(constant_circuit=None, circuits=transpiled_circuits)
        else:
            raise TypeError("Unknown measurement type")

    return QuantumProgram(
        measurement=recreate_measurement(quantum_program, transpiled_circuits),
        input_parameter_names=quantum_program.input_parameter_names(),
    )
