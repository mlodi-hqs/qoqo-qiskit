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
from qoqo import measurements

from .post_processing import _transform_job_result


class QueuedCircuitRun:
    """Queued Result of the circuit."""

    def __init__(
        self,
        job: Job,
        memory: bool,
        sim_type: str,
        registers_info: Tuple[
            Dict[str, int],
            Dict[str, List[List[bool]]],
            Dict[str, List[List[float]]],
            Dict[str, List[List[complex]]],
        ],
    ) -> None:
        """Initialise the QueuedCircuitRun class.

        Args:
            job (Job): The job that is run.
            memory (bool): True if the result is meant to be read via `job.get_memory()` instead
                of `job.get_counts()`.
            sim_type (str): The simulation type. This can be "automatic", "statevector"
                or "density_matrix".
            registers_info (Tuple[Any]): The initially setup registers.
        """
        self._job: Job = job
        self._memory: bool = memory
        self._sim_type: str = sim_type
        self._registers_info: Tuple[
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
                self._qoqo_result = _transform_job_result(
                    self._memory,
                    self._sim_type,
                    result,
                    self._registers_info[0],
                    self._registers_info[1],
                    self._registers_info[2],
                    self._registers_info[3],
                )
                return self._qoqo_result
            elif status == JobStatus.ERROR:
                RuntimeError("The job failed.")
            else:
                RuntimeError("The job was cancelled.")
        else:
            return None


class QueuedProgramRun:
    """Queued Result of the measurement."""

    def __init__(self, measurement: Any, queued_circuits: List[QueuedCircuitRun]) -> None:
        """Initialise the QueuedProgramRun class.

        Args:
            measurement (qoqo.measurements): The qoqo Measurement to run.
            queued_circuits (List[QueuedCircuitRun]): The list of associated queued circuits.
        """
        self._measurement = measurement
        self._queued_circuits: List[QueuedCircuitRun] = queued_circuits

    def to_json(self) -> str:
        """Convert self to a JSON string.

        Returns:
            str: self as a JSON string.
        """
        pass

    @staticmethod
    def from_json(string: str) -> QueuedProgramRun:
        """Convert a JSON string to an instance of QueuedProgramRun.

        Args:
            string (str): JSON string to convert.

        Returns:
            QueuedProgramRun: The converted instance.
        """
        pass

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
                    Dict[str, List[List[complex]]]]]: Result if the run was successful.

        Raises:
            RuntimeError: The job failed or was cancelled.
        """
        pass
