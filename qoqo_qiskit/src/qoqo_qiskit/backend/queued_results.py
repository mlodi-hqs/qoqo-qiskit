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
"""Queued Jobs."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple, Union

from qiskit.providers import Job, JobStatus
from qiskit_ibm_runtime import QiskitRuntimeService
from qoqo import measurements  # type:ignore

from ..models import Registers, RegistersWithLengths
from .post_processing import _transform_job_result
from .utils import is_valid_uuid4


class QueuedCircuitRun:
    """Queued Result of the circuit."""

    def __init__(
        self,
        job: Job,
        memory: bool,
        sim_type: str,
        registers_info: Tuple[
            Dict[str, int],
            Dict[str, int],
            Dict[str, int],
            Dict[str, List[List[bool]]],
            Dict[str, List[List[float]]],
            Dict[str, List[List[complex]]],
        ],
        res_index: Optional[int] = 0,
    ) -> None:
        """Initialise the QueuedCircuitRun class.

        Args:
            job (Job): The job that is run.
            memory (bool): True if the result is meant to be read via `job.get_memory()` instead
                of `job.get_counts()`.
            sim_type (str): The simulation type. This can be "automatic", "statevector"
                or "density_matrix".
            registers_info (Tuple[Any]): The initially setup registers.
            res_index (Optional[int]): The index of the ExperimentalResult in Result.results.
                Defaults to 0. It can be relevant in case the circuit has been run as part of
                a list.
        """
        self._job: Job = job
        self._memory: bool = memory
        self._sim_type: str = sim_type
        self._registers_info: Tuple[
            Dict[str, int],
            Dict[str, int],
            Dict[str, int],
            Dict[str, List[List[bool]]],
            Dict[str, List[List[float]]],
            Dict[str, List[List[complex]]],
        ] = registers_info
        self._qoqo_result: Optional[
            Tuple[
                Dict[str, List[List[bool]]],
                Dict[str, List[List[float]]],
                Dict[str, List[List[complex]]],
            ]
        ] = None
        self._res_index: Optional[int] = res_index

    def to_json(self) -> str:
        """Convert self to a JSON string.

        Returns:
            str: self as a JSON string.
        """
        json_dict = {
            "job_id": self._job.job_id(),
            "memory": self._memory,
            "sim_type": self._sim_type,
            "registers_info": self._registers_info,
            "qoqo_result": self._qoqo_result,
            "res_index": self._res_index,
        }

        return json.dumps(json_dict)

    @staticmethod
    def from_json(string: str) -> QueuedCircuitRun:
        """Convert a JSON string to an instance of QueuedCircuitRun.

        Args:
            string (str): JSON string to convert.

        Returns:
            QueuedCircuitRun: The converted instance.
        """
        json_dict = json.loads(string)

        # If id is valid uuid4, then the job was locally executed via qiskit_aer.AerSimulator()
        if is_valid_uuid4(json_dict["job_id"]):
            raise ValueError(
                "The job was executed locally via qiskit_aer.AerSimulator(). "
                "Retrieval is not possible."
            )
        else:
            service = QiskitRuntimeService()
            job = service.job(json_dict["job_id"])

        instance = QueuedCircuitRun(
            job=job,
            memory=json_dict["memory"],
            sim_type=json_dict["sim_type"],
            registers_info=json_dict["registers_info"],
        )
        if json_dict["qoqo_result"] is not None:
            instance._qoqo_result = json_dict["qoqo_result"]
        if json_dict["res_index"] is not None:
            instance._res_index = json_dict["res_index"]

        return instance

    def poll_result(
        self,
    ) -> Optional[
        Tuple[
            Dict[str, List[List[bool]]],
            Dict[str, List[List[float]]],
            Dict[str, List[List[complex]]],
        ]
    ]:
        """Poll the result.

        Returns:
            Tuple[Dict[str, List[List[bool]]],
                  Dict[str, List[List[float]]],
                  Dict[str, List[List[complex]]]]: Result if the run was successful.

        Raises:
            RuntimeError: The job failed or was cancelled.
        """
        if self._qoqo_result is not None:
            return self._qoqo_result
        if self._job.in_final_state():
            status = self._job.status()
            if status == JobStatus.DONE:
                result = self._job.result()
                modeled = RegistersWithLengths(
                    Registers(
                        bit_register_dict=self._registers_info[3],
                        float_register_dict=self._registers_info[4],
                        complex_register_dict=self._registers_info[5],
                    ),
                    bit_regs_lengths=self._registers_info[0],
                    float_regs_lengths=self._registers_info[1],
                    complex_regs_lengths=self._registers_info[2],
                )
                self._qoqo_result = _transform_job_result(
                    self._memory, self._sim_type, result, modeled, self._res_index
                )
                return self._qoqo_result
            elif status == JobStatus.ERROR:
                raise RuntimeError("The job failed.")
            else:
                raise RuntimeError("The job was cancelled.")
        else:
            return None


class QueuedProgramRun:
    """Queued Result of the measurement."""

    def __init__(self, measurement: Any, queued_circuits: List[QueuedCircuitRun]) -> None:
        """Initialise the QueuedProgramRun class.

        Args:
            measurement (qoqo.measurements): The qoqo Measurement to run.
            queued_circuits (List[QueuedCircuitRun]): The list of associated queued circuits.

        Raises:
            TypeError: The measurement type is unknown.
        """
        if (
            isinstance(measurement, measurements.PauliZProduct)
            or isinstance(measurement, measurements.CheatedPauliZProduct)
            or isinstance(measurement, measurements.Cheated)
            or isinstance(measurement, measurements.ClassicalRegister)
        ):
            self._measurement = measurement
        else:
            raise TypeError("Unknown measurement type.")
        self._queued_circuits: List[QueuedCircuitRun] = queued_circuits
        self._registers: Tuple[
            Dict[str, List[List[bool]]],
            Dict[str, List[List[float]]],
            Dict[str, List[List[complex]]],
        ] = ({}, {}, {})
        for circuit in self._queued_circuits:
            if circuit._qoqo_result is not None:
                for key, value_bools in circuit._qoqo_result[0].items():
                    if key in self._registers[0]:
                        self._registers[0][key].extend(value_bools)
                    else:
                        self._registers[0][key] = value_bools
                for key, value_floats in circuit._qoqo_result[1].items():
                    if key in self._registers[1]:
                        self._registers[1][key].extend(value_floats)
                    else:
                        self._registers[1][key] = value_floats
                for key, value_complexes in circuit._qoqo_result[2].items():
                    if key in self._registers[2]:
                        self._registers[2][key].extend(value_complexes)
                    else:
                        self._registers[2][key] = value_complexes

    def to_json(self) -> str:
        """Convert self to a JSON string.

        Returns:
            str: self as a JSON string.

        Raises:
            TypeError: The measurement type is unknown.
        """
        queued_circuits_serialised: List[str] = []
        for circuit in self._queued_circuits:
            queued_circuits_serialised.append(circuit.to_json())

        if isinstance(self._measurement, measurements.PauliZProduct):
            measurement_type = "PauliZProduct"
        elif isinstance(self._measurement, measurements.CheatedPauliZProduct):
            measurement_type = "CheatedPauliZProduct"
        elif isinstance(self._measurement, measurements.Cheated):
            measurement_type = "Cheated"
        elif isinstance(self._measurement, measurements.ClassicalRegister):
            measurement_type = "ClassicalRegister"
        else:
            raise TypeError("Unknown measurement type")

        json_dict = {
            "measurement_type": measurement_type,
            "measurement": self._measurement.to_json(),
            "queued_circuits": queued_circuits_serialised,
            "registers": self._registers,
        }

        return json.dumps(json_dict)

    @staticmethod
    def from_json(string: str) -> QueuedProgramRun:
        """Convert a JSON string to an instance of QueuedProgramRun.

        Args:
            string (str): JSON string to convert.

        Raises:
            TypeError: The measurement type is unknown.

        Returns:
            QueuedProgramRun: The converted instance.
        """
        json_dict = json.loads(string)

        queued_circuits_deserialised: List[QueuedCircuitRun] = []
        registers: Tuple[
            Dict[str, List[List[bool]]],
            Dict[str, List[List[float]]],
            Dict[str, List[List[complex]]],
        ] = ({}, {}, {})
        for circuit in json_dict["queued_circuits"]:
            circ_instance = QueuedCircuitRun.from_json(circuit)
            queued_circuits_deserialised.append(circ_instance)
            if circ_instance._qoqo_result is not None:
                for key, value_bools in circ_instance._qoqo_result[0].items():
                    if key in registers[0]:
                        registers[0][key].extend(value_bools)
                    else:
                        registers[0][key] = value_bools
                for key, value_floats in circ_instance._qoqo_result[1].items():
                    if key in registers[1]:
                        registers[1][key].extend(value_floats)
                    else:
                        registers[1][key] = value_floats
                for key, value_complexes in circ_instance._qoqo_result[2].items():
                    if key in registers[2]:
                        registers[2][key].extend(value_complexes)
                    else:
                        registers[2][key] = value_complexes

        if json_dict["measurement_type"] == "PauliZProduct":
            measurement = measurements.PauliZProduct.from_json(json_dict["measurement"])
        elif json_dict["measurement_type"] == "CheatedPauliZProduct":
            measurement = measurements.CheatedPauliZProduct.from_json(json_dict["measurement"])
        elif json_dict["measurement_type"] == "Cheated":
            measurement = measurements.Cheated.from_json(json_dict["measurement"])
        elif json_dict["measurement_type"] == "ClassicalRegister":
            measurement = measurements.ClassicalRegister.from_json(json_dict["measurement"])
        else:
            raise TypeError("Unknown measurement type")

        instance = QueuedProgramRun(measurement, queued_circuits_deserialised)
        instance._registers = registers
        return instance

    def poll_result(
        self,
    ) -> Optional[
        Union[
            Tuple[
                Dict[str, List[List[bool]]],
                Dict[str, List[List[float]]],
                Dict[str, List[List[complex]]],
            ]
        ]
    ]:
        """Poll the result.

        Returns:
            Union[Tuple[Dict[str, List[List[bool]]],
                    Dict[str, List[List[float]]],
                    Dict[str, List[List[complex]]]]]: Result if all runs were successful.

        Raises:
            RuntimeError: The jobs failed or were cancelled.
        """
        all_finished = [False] * len(self._queued_circuits)
        for i, queued_circuit in enumerate(self._queued_circuits):
            res = queued_circuit.poll_result()
            if res is not None:
                for key, value_bools in res[0].items():
                    if key in self._registers[0]:
                        self._registers[0][key].extend(value_bools)
                    else:
                        self._registers[0][key] = value_bools
                for key, value_floats in res[1].items():
                    if key in self._registers[1]:
                        self._registers[1][key].extend(value_floats)
                    else:
                        self._registers[1][key] = value_floats
                for key, value_complexes in res[2].items():
                    if key in self._registers[2]:
                        self._registers[2][key].extend(value_complexes)
                    else:
                        self._registers[2][key] = value_complexes
                all_finished[i] = True

        if not all(all_finished):
            return None
        else:
            if isinstance(self._measurement, measurements.ClassicalRegister):
                return self._registers
            else:
                return self._measurement.evaluate(
                    self._registers[0], self._registers[1], self._registers[2]
                )
