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

from dataclasses import astuple
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from qiskit import QuantumCircuit
from qiskit.providers import Backend
from qiskit.providers.job import Job
from qiskit_aer import AerSimulator
from qoqo import Circuit, QuantumProgram
from qoqo.measurements import ClassicalRegister  # type:ignore

from qoqo_qiskit.backend.queued_results import QueuedCircuitRun, QueuedProgramRun
from qoqo_qiskit.interface import to_qiskit_circuit

from ..models import RegistersWithLengths, Registers
from .post_processing import _transform_job_result


class QoqoQiskitBackend:
    """Run a Qoqo QuantumProgram on a Qiskit backend."""

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

    # Internal _run_circuit method
    def _run_circuit(self, circuit: Circuit) -> Tuple[
        Job,
        str,
        RegistersWithLengths,
    ]:
        if not circuit.__class__.__name__ == "Circuit":
            raise TypeError("The input is not a valid Qoqo Circuit instance.")

        output_registers = self._set_up_registers(circuit)

        (compiled_circuit, run_options) = self._compile_circuit(circuit)

        self._handle_errors(run_options)

        (shots, sim_type) = self._handle_simulation_options(run_options, compiled_circuit)

        job = self._job_execution(compiled_circuit, shots)

        return (job, sim_type, output_registers)

    def _run_circuit_list(
        self, circuit_list: List[Circuit]
    ) -> Tuple[Job, str, List[RegistersWithLengths]]:
        if not isinstance(circuit_list, List):
            raise TypeError("The input is not a valid list of Qoqo Circuit instances.")
        if len(circuit_list) == 0:
            raise ValueError("The input is an empty list of Qoqo Circuit instances.")

        compiled_circuits_list: List[Circuit] = []
        output_registers_list: List[RegistersWithLengths] = []
        sim_type_list: Optional[str] = None
        shots_list: Optional[int] = None
        for circuit in circuit_list:
            output_registers = self._set_up_registers(circuit)

            (compiled_circuit, run_options) = self._compile_circuit(circuit)

            self._handle_errors(run_options)

            (shots, sim_type) = self._handle_simulation_options(run_options, compiled_circuit)

            # Raise errors if some circuits have different sim types or shots
            if sim_type_list is None:
                sim_type_list = sim_type
            else:
                if sim_type != sim_type_list:
                    raise ValueError(
                        "The input is a list of Qoqo Circuits with different simulation types."
                    )
            if shots_list is None:
                shots_list = shots
            else:
                if shots != shots_list:
                    raise ValueError(
                        "The input is a list of Qoqo Circuits with different number of shots."
                    )

            compiled_circuits_list.append(compiled_circuit)
            output_registers_list.append(output_registers)

        job = self._job_execution(compiled_circuits_list, cast(int, shots_list))

        return (job, cast(str, sim_type_list), output_registers_list)

    def _set_up_registers(
        self,
        circuit: Circuit,
    ) -> RegistersWithLengths:
        output_registers = RegistersWithLengths()

        for bit_def in circuit.filter_by_tag("DefinitionBit"):
            output_registers.clas_regs_lengths[bit_def.name()] = bit_def.length()
            if bit_def.is_output():
                output_registers.registers.bit_register_dict[bit_def.name()] = []
        for float_def in circuit.filter_by_tag("DefinitionFloat"):
            if float_def.is_output():
                output_registers.registers.float_register_dict[float_def.name()] = cast(
                    List[List[float]], []
                )
        for complex_def in circuit.filter_by_tag("DefinitionComplex"):
            if complex_def.is_output():
                output_registers.registers.complex_register_dict[complex_def.name()] = cast(
                    List[List[complex]], []
                )
        return output_registers

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
        input_to_send: Union[Circuit, List[Circuit]],
        shots: int,
    ) -> Job:
        job = self.qiskit_backend.run(input_to_send, shots=shots, memory=self.memory)
        return job

    def run_circuit(
        self,
        circuit: Circuit,
    ) -> Tuple[
        Dict[str, List[List[bool]]],
        Dict[str, List[List[float]]],
        Dict[str, List[List[complex]]],
    ]:
        """Run a Circuit on a Qiskit backend.

        The default number of shots for the simulation is 200.
        Any kind of Measurement, Statevector or DensityMatrix instruction only works as intended if
        they are the last instructions in the Circuit.
        Currently only one simulation is performed, meaning different measurements on different
        registers are not supported.

        Args:
            circuit (Circuit): the Circuit to run.

        Returns:
            Tuple[Dict[str, List[List[bool]]],\
                  Dict[str, List[List[float]]],\
                  Dict[str, List[List[complex]]]]: bit, float and complex registers dictionaries.

        Raises:
            ValueError: Incorrect Measurement or Pragma operations.
        """
        (job, sim_type, output_registers) = self._run_circuit(circuit)

        result = job.result()

        # Result transformation
        return _transform_job_result(
            self.memory,
            sim_type,
            result,
            output_registers,
        )

    def run_circuit_list(
        self,
        circuits: List[Circuit],
    ) -> Tuple[
        Dict[str, List[List[bool]]],
        Dict[str, List[List[float]]],
        Dict[str, List[List[complex]]],
    ]:
        """Run a list of Circuit instances on a Qiskit backend.

        The default number of shots for the simulation is 200.
        Any kind of Measurement, Statevector or DensityMatrix instruction only works as intended if
        they are the last instructions in the Circuit.
        Currently only one simulation is performed, meaning different measurements on different
        registers are not supported.

        Args:
            circuits (List[Circuit]): the list of Circuit instances to run.

        Returns:
            Tuple[Dict[str, List[List[bool]]],\
                  Dict[str, List[List[float]]],\
                  Dict[str, List[List[complex]]]]: bit, float and complex registers dictionaries.

        Raises:
            ValueError: Incorrect Measurement or Pragma operations or incompatible run options\
                between different circuits.
        """
        (job, sim_type, output_registers_list) = self._run_circuit_list(circuits)

        result = job.result()

        # Result transformation
        return _transform_job_result(
            self.memory,
            sim_type,
            result,
            output_registers_list,
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
            circuit (Circuit): the Circuit to run.

        Returns:
            QueuedCircuitRun
        """
        (
            job,
            sim_type,
            output_registers,
        ) = self._run_circuit(circuit)

        return QueuedCircuitRun(job, self.memory, sim_type, output_registers.to_flat_tuple())

    def run_circuit_list_queued(self, circuits: List[Circuit]) -> List[QueuedCircuitRun]:
        """Run a list of Circuit instances on a Qiskit backend and return a list of queued Runs.

        The default number of shots for the simulation is 200.
        Any kind of Measurement, Statevector or DensityMatrix instruction only works as intended if
        they are the last instructions in the Circuit.
        Currently only one simulation is performed, meaning different measurements on different
        registers are not supported.

        Args:
            circuits (List[Circuit]): the list of Circuit instances to run.

        Returns:
            List[QueuedCircuitRun]
        """
        (
            job,
            sim_type,
            output_registers,
        ) = self._run_circuit_list(circuits)

        return [
            QueuedCircuitRun(job, self.memory, sim_type, reg.to_flat_tuple(), res_index)
            for res_index, reg in enumerate(output_registers)
        ]

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
        output_registers = Registers()

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

            for key, value_bools in tmp_bit_register_dict.items():
                if key in output_registers.bit_register_dict:
                    output_registers.bit_register_dict[key].extend(value_bools)
                else:
                    output_registers.bit_register_dict[key] = value_bools
            for key, value_floats in tmp_float_register_dict.items():
                if key in output_registers.float_register_dict:
                    output_registers.float_register_dict[key].extend(value_floats)
                else:
                    output_registers.float_register_dict[key] = value_floats
            for key, value_complexes in tmp_complex_register_dict.items():
                if key in output_registers.complex_register_dict:
                    output_registers.complex_register_dict[key].extend(value_complexes)
                else:
                    output_registers.complex_register_dict[key] = value_complexes

        return astuple(output_registers)

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

    def run_program(
        self, program: QuantumProgram, params_values: Union[List[float], List[List[float]]]
    ) -> Optional[
        List[
            Union[
                Tuple[
                    Dict[str, List[List[bool]]],
                    Dict[str, List[List[float]]],
                    Dict[str, List[List[complex]]],
                ],
                Dict[str, float],
            ]
        ]
    ]:
        """Run a qoqo quantum program on an IBM backend multiple times.

        It can handle QuantumProgram instances containing any kind of measurement. The list of
        lists of parameters will be used to call `program.run(self, params)` or
        `program.run_registers(self, params)` as many times as the number of sublists.
        The return type will change accordingly.

        If no parameters values are provided, a normal call `program.run(self, [])` call
        will be executed.

        Args:
            program (QuantumProgram): the qoqo quantum program to run.
            params_values (Union[List[float], List[List[float]]]): the parameters values to pass
                to the quantum program.

        Returns:
            Optional[
                List[
                    Union[
                        Tuple[
                            Dict[str, List[List[bool]]],
                            Dict[str, List[List[float]]],
                            Dict[str, List[List[complex]]],
                        ],
                        Dict[str, float],
                    ]
                ]
            ]: list of dictionaries (or tuples of dictionaries) containing the
                run results.
        """
        returned_results = []

        if isinstance(program.measurement(), ClassicalRegister):
            if not params_values:
                returned_results.append(program.run_registers(self, []))
            if isinstance(params_values[0], list):
                for params in params_values:
                    returned_results.append(program.run_registers(self, params))
            else:
                return program.run_registers(self, params_values)
        else:
            if not params_values:
                returned_results.append(program.run(self, []))
            if isinstance(params_values[0], list):
                for params in params_values:
                    returned_results.append(program.run(self, params))
            else:
                return program.run(self, params_values)

        return returned_results

    def run_measurement_queued(self, measurement: Any) -> QueuedProgramRun:
        """Run a qoqo measurement on a Qiskit backend and return a queued Job Result.

        The default number of shots for the simulation is 200.
        Any kind of Measurement, Statevector or DensityMatrix instruction only works as intended if
        they are the last instructions in the Circuit.
        Currently only one simulation is performed, meaning different measurements on different
        registers are not supported.

        Args:
            measurement (qoqo.measurements): the measurement to run.

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

    def run_program_queued(
        self, program: QuantumProgram, params_values: Union[List[float], List[List[float]]]
    ) -> List[QueuedProgramRun]:
        """Run a qoqo quantum program on a AWS backend multiple times return a list of queued Jobs.

        This effectively performs the same operations as `run_program` but returns
        queued results.


        Args:
            program (QuantumProgram): the qoqo quantum program to run.
            params_values (Union[List[float], List[List[float]]]): the parameters values to pass
                to the quantum program.

        Raises:
            ValueError: incorrect length of params_values compared to program's input
                parameter names.

        Returns:
            List[QueuedProgramRun]]
        """
        queued_runs: List[QueuedProgramRun] = []
        input_parameter_names = program.input_parameter_names()

        if not params_values:
            if input_parameter_names:
                raise ValueError(
                    "Wrong parameters value: no parameters values provided but"
                    f" input QuantumProgram has {len(input_parameter_names)}"
                    " input parameter names."
                )
            queued_runs.append(self.run_measurement_queued(program.measurement()))
        if isinstance(params_values[0], list):
            for params in params_values:
                if len(params) != len(input_parameter_names):
                    raise ValueError(
                        f"Wrong number of parameters {len(input_parameter_names)} parameters"
                        f" expected {len(params)} parameters given."
                    )
                substituted_parameters = dict(zip(input_parameter_names, params))
                measurement = program.measurement().substitute_parameters(substituted_parameters)
                queued_runs.append(self.run_measurement_queued(measurement))
        else:
            if len(params_values) != len(input_parameter_names):
                raise ValueError(
                    f"Wrong number of parameters {len(input_parameter_names)} parameters"
                    f" expected {len(params_values)} parameters given."
                )
            substituted_parameters = dict(zip(input_parameter_names, params_values))
            measurement = program.measurement().substitute_parameters(substituted_parameters)
            queued_runs.append(self.run_measurement_queued(measurement))

        return queued_runs
