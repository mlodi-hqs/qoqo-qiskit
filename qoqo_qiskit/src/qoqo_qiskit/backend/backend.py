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
"""Qoqo-qiskit backend for simulation purposes."""

from typing import Any, Dict, List, Optional, Tuple, cast

from qiskit import QuantumCircuit, execute
from qiskit.providers import Backend
from qiskit.providers.job import Job
from qiskit_aer import AerSimulator
from qoqo import Circuit

from qoqo_qiskit.backend.queued_results import QueuedCircuitRun, QueuedProgramRun
from qoqo_qiskit.interface import to_qiskit_circuit

from .post_processing import _transform_job_result


class QoqoQiskitBackend:
    """Simulate a Qoqo QuantumProgram on a Qiskit backend."""

    def __init__(
        self,
        qiskit_backend: Backend = None,
        memory: bool = False,
        compilation: bool = True,
    ) -> None:
        """Init for Qiskit backend settings.

        Args:
            qiskit_backend (Backend): Qiskit backend instance to use for the simulation.
            memory (bool): Whether the output will return the actual single shots instead
                           of an equivalent sequence taken from a result summary.
            compilation (bool): Whether the qiskit `compiler` should be used instead of `run`.

        Raises:
            TypeError: the input is not a valid Qiskit Backend instance.
        """
        if qiskit_backend is None:
            self.qiskit_backend = AerSimulator()
        elif not isinstance(qiskit_backend, Backend):
            raise TypeError("The input is not a valid Qiskit Backend instance.")
        else:
            self.qiskit_backend = qiskit_backend
        self.memory = memory
        self.compilation = compilation

    # Internal _run_circuit method, for async support
    def _run_circuit(self, circuit: Circuit) -> Tuple[
        Job,
        str,
        Dict[str, int],
        Dict[str, List[List[bool]]],
        Dict[str, List[List[float]]],
        Dict[str, List[List[complex]]],
    ]:
        if not isinstance(circuit, Circuit):
            raise TypeError("The input is not a valid Qoqo Circuit instance.")

        # Initial register setup
        (
            clas_regs_sizes,
            output_bit_register_dict,
            output_float_register_dict,
            output_complex_register_dict,
        ) = self._setup_registers(circuit)

        # Circuit compilation
        (compiled_circuit, run_options) = self._compile_circuit(circuit)

        # Error handling
        self._handle_errors(run_options)

        # Handle simulation Options
        (shots, sim_type) = self._handle_simulation_options(run_options, compiled_circuit)

        # Job Execution
        job = self._job_execution(compiled_circuit, shots)

        return (
            job,
            sim_type,
            clas_regs_sizes,
            output_bit_register_dict,
            output_float_register_dict,
            output_complex_register_dict,
        )

    def _setup_registers(
        self,
        circuit: Circuit,
    ) -> Tuple[
        Dict[str, int],
        Dict[str, List[List[bool]]],
        Dict[str, List[List[float]]],
        Dict[str, List[List[complex]]],
    ]:
        clas_regs_sizes: Dict[str, int] = {}

        # Initializing the classical registers for calculation and output
        internal_bit_register_dict: Dict[str, List[bool]] = {}
        internal_float_register_dict: Dict[str, List[float]] = {}
        internal_complex_register_dict: Dict[str, List[complex]] = {}

        output_bit_register_dict: Dict[str, List[List[bool]]] = {}
        output_float_register_dict: Dict[str, List[List[float]]] = {}
        output_complex_register_dict: Dict[str, List[List[complex]]] = {}

        for bit_def in circuit.filter_by_tag("DefinitionBit"):
            internal_bit_register_dict[bit_def.name()] = [False for _ in range(bit_def.length())]
            clas_regs_sizes[bit_def.name()] = bit_def.length()
            if bit_def.is_output():
                output_bit_register_dict[bit_def.name()] = []
        for float_def in circuit.filter_by_tag("DefinitionFloat"):
            internal_float_register_dict[float_def.name()] = [
                0.0 for _ in range(float_def.length())
            ]
            if float_def.is_output():
                output_float_register_dict[float_def.name()] = cast(List[List[float]], [])
        for complex_def in circuit.filter_by_tag("DefinitionComplex"):
            internal_complex_register_dict[complex_def.name()] = [
                complex(0.0) for _ in range(complex_def.length())
            ]
            if complex_def.is_output():
                output_complex_register_dict[complex_def.name()] = cast(List[List[complex]], [])
        return (
            clas_regs_sizes,
            output_bit_register_dict,
            output_float_register_dict,
            output_complex_register_dict,
        )

    def _compile_circuit(
        self,
        circuit: Circuit,
    ) -> Tuple[QuantumCircuit, Dict[str, Any]]:
        try:
            defs = circuit.definitions()
            doubles = [defs[0]]
            for op in defs:
                if op not in doubles:
                    doubles.append(op)
            debugged_circuit = Circuit()
            for def_bit in doubles:
                debugged_circuit += def_bit
            for op in circuit:
                if op not in doubles:
                    debugged_circuit += op
        except IndexError:
            debugged_circuit = circuit

        # Qiskit conversion
        res = to_qiskit_circuit(debugged_circuit)
        compiled_circuit: QuantumCircuit = res[0]
        run_options: Dict[str, Any] = res[1]

        return compiled_circuit, run_options

    def _handle_errors(
        self,
        run_options: Dict[str, Any],
    ) -> None:
        # Raise ValueError:
        #   - if no measurement of any kind and no Pragmas are involved
        if (
            not run_options["MeasurementInfo"]
            and not run_options["SimulationInfo"]["PragmaGetStateVector"]
            and not run_options["SimulationInfo"]["PragmaGetDensityMatrix"]
        ):
            raise ValueError(
                "The Circuit does not contain Measurement, PragmaGetStateVector"
                " or PragmaGetDensityMatrix operations. Simulation not possible."
            )
        #   - if both StateVector and DensityMatrix pragmas are involved
        if (
            run_options["SimulationInfo"]["PragmaGetStateVector"]
            and run_options["SimulationInfo"]["PragmaGetDensityMatrix"]
        ):
            raise ValueError(
                "The Circuit contains both a PragmaGetStateVector"
                " and a PragmaGetDensityMatrix instruction. Simulation not possible."
            )
        #   - if more than 1 type of measurement is involved
        if len(run_options["MeasurementInfo"]) > 1:
            raise ValueError("Only input Circuits containing one type of measurement.")

    def _handle_simulation_options(
        self,
        run_options: Dict[str, Any],
        compiled_circuit: QuantumCircuit,
    ) -> Tuple[int, str]:
        shots = 200
        custom_shots = 0
        sim_type = "automatic"
        if run_options["SimulationInfo"]["PragmaGetStateVector"]:
            compiled_circuit.save_statevector()
            sim_type = "statevector"
        elif run_options["SimulationInfo"]["PragmaGetDensityMatrix"]:
            compiled_circuit.save_density_matrix()
            sim_type = "density_matrix"
        if "PragmaRepeatedMeasurement" in run_options["MeasurementInfo"]:
            for el in run_options["MeasurementInfo"]["PragmaRepeatedMeasurement"]:
                if el[1] > custom_shots:
                    custom_shots = el[1]
        if "PragmaSetNumberOfMeasurements" in run_options["SimulationInfo"]:
            for el in run_options["SimulationInfo"]["PragmaSetNumberOfMeasurements"]:
                if el[1] > custom_shots:
                    custom_shots = el[1]
        if custom_shots != 0:
            shots = custom_shots
        return shots, sim_type

    def _job_execution(
        self,
        compiled_circuit: Circuit,
        shots: int,
    ) -> Job:
        if self.compilation:
            job = execute(compiled_circuit, self.qiskit_backend, shots=shots, memory=self.memory)
        else:
            job = self.qiskit_backend.run(compiled_circuit, shots=shots)
        return job

    def run_circuit(
        self,
        circuit: Circuit,
    ) -> Tuple[
        Dict[str, List[List[bool]]],
        Dict[str, List[List[float]]],
        Dict[str, List[List[complex]]],
    ]:
        """Simulate a Circuit on a Qiskit backend.

        The default number of shots for the simulation is 200.
        Any kind of Measurement, Statevector or DensityMatrix instruction only works as intended if
        they are the last instructions in the Circuit.
        Currently only one simulation is performed, meaning different measurements on different
        registers are not supported.

        Args:
            circuit (Circuit): the Circuit to simulate.

        Returns:
            Tuple[Dict[str, List[List[bool]]],\
                  Dict[str, List[List[float]]],\
                  Dict[str, List[List[complex]]]]: bit, float and complex registers dictionaries.

        Raises:
            ValueError: Incorrect Measurement or Pragma operations.
        """
        (
            job,
            sim_type,
            clas_regs_sizes,
            output_bit_register_dict,
            output_float_register_dict,
            output_complex_register_dict,
        ) = self._run_circuit(circuit)

        result = job.result()

        # Result transformation
        return _transform_job_result(
            self.memory,
            sim_type,
            result,
            clas_regs_sizes,
            output_bit_register_dict,
            output_float_register_dict,
            output_complex_register_dict,
        )

    def run_circuit_queued(
        self,
        circuit: Circuit,
    ) -> QueuedCircuitRun:
        """Run a Circuit on a Qiskit backend and return a queued Run.

        The default number of shots for the simulation is 200.
        Any kind of Measurement, Statevector or DensityMatrix instruction only works as intended if
        they are the last instructions in the Circuit.
        Currently only one simulation is performed, meaning different measurements on different
        registers are not supported.

        Args:
            circuit (Circuit): the Circuit to simulate.

        Returns:
            QueuedCircuitRun
        """
        (
            job,
            sim_type,
            clas_regs_sizes,
            output_bit_register_dict,
            output_float_register_dict,
            output_complex_register_dict,
        ) = self._run_circuit(circuit)

        register_info: Tuple[
            Dict[str, int],
            Dict[str, List[List[bool]]],
            Dict[str, List[List[float]]],
            Dict[str, List[List[complex]]],
        ] = (
            clas_regs_sizes,
            output_bit_register_dict,
            output_float_register_dict,
            output_complex_register_dict,
        )

        return QueuedCircuitRun(job, self.memory, sim_type, register_info)

    def run_measurement_registers(
        self,
        measurement: Any,
    ) -> Tuple[
        Dict[str, List[List[bool]]],
        Dict[str, List[List[float]]],
        Dict[str, List[List[complex]]],
    ]:
        """Run all circuits of a measurement with the Qiskit backend.

        Args:
            measurement: The measurement that is run.

        Returns:
            Tuple[Dict[str, List[List[bool]]],\
                  Dict[str, List[List[float]]],\
                  Dict[str, List[List[complex]]]]
        """
        constant_circuit = measurement.constant_circuit()
        output_bit_register_dict: Dict[str, List[List[bool]]] = {}
        output_float_register_dict: Dict[str, List[List[float]]] = {}
        output_complex_register_dict: Dict[str, List[List[complex]]] = {}

        for circuit in measurement.circuits():
            if constant_circuit is None:
                run_circuit = circuit
            else:
                run_circuit = constant_circuit + circuit

            (
                tmp_bit_register_dict,
                tmp_float_register_dict,
                tmp_complex_register_dict,
            ) = self.run_circuit(run_circuit)

            output_bit_register_dict.update(tmp_bit_register_dict)
            output_float_register_dict.update(tmp_float_register_dict)
            output_complex_register_dict.update(tmp_complex_register_dict)

        return (
            output_bit_register_dict,
            output_float_register_dict,
            output_complex_register_dict,
        )

    def run_measurement(
        self,
        measurement: Any,
    ) -> Optional[Dict[str, float]]:
        """Run a circuit with the Qiskit backend.

        Args:
            measurement: The measurement that is run.

        Returns:
            Optional[Dict[str, float]]
        """
        (
            output_bit_register_dict,
            output_float_register_dict,
            output_complex_register_dict,
        ) = self.run_measurement_registers(measurement)

        return measurement.evaluate(
            output_bit_register_dict,
            output_float_register_dict,
            output_complex_register_dict,
        )

    def run_measurement_queued(self, measurement: Any) -> QueuedProgramRun:
        """Run a qoqo measurement on a Qiskit backend and return a queued Job Result.

        The default number of shots for the simulation is 200.
        Any kind of Measurement, Statevector or DensityMatrix instruction only works as intended if
        they are the last instructions in the Circuit.
        Currently only one simulation is performed, meaning different measurements on different
        registers are not supported.

        Args:
            measurement (qoqo.measurements): the measurement to simulate.

        Returns:
            QueuedProgramRun
        """
        queued_circuits = []
        constant_circuit = measurement.constant_circuit()
        for circuit in measurement.circuits():
            if constant_circuit is None:
                run_circuit = circuit
            else:
                run_circuit = constant_circuit + circuit

            queued_circuits.append(self.run_circuit_queued(run_circuit))
        return QueuedProgramRun(measurement, queued_circuits)
