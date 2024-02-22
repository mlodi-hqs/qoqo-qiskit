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

from qiskit.providers import Job, JobStatus

from .post_processing import _transform_job_result

from typing import Any, List, Tuple, Dict, Optional


class QueuedCircuitRun:
    """Queued Result of the circuit."""

    def __init__(
        self,
        job: Job,
        memory: bool,
        sim_type: str,
        register_info: Tuple[
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
            register_info (Tuple[Any]): The initially setup registers.
                These will be updated with the job result.
        """
        self._job: Job = job
        self._memory: bool = memory
        self._sim_type: str = sim_type
        self._initially_setup_registers: Tuple[
            Dict[str, int],
            Dict[str, List[List[bool]]],
            Dict[str, List[List[float]]],
            Dict[str, List[List[complex]]],
        ] = register_info
        self._qoqo_result: Optional[
            Tuple[
                Dict[str, List[List[bool]]],
                Dict[str, List[List[float]]],
                Dict[str, List[List[complex]]],
            ]
        ] = None

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
                    self._initially_setup_registers[0],
                    self._initially_setup_registers[1],
                    self._initially_setup_registers[2],
                    self._initially_setup_registers[3],
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
            measurement: the qoqo Measurement to run
            queued_circuits: the list of associated queued circuits
        """
        pass
