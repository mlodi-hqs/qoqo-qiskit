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

from qiskit.providers import Job

from typing import Any, List, Tuple, Dict, Optional


class QueuedCircuitRun:
    """Queued Result of the circuit."""

    def __init__(self, job: Job) -> None:
        """Initialise the QueuedCircuitRun class.

        Args:
            job: The job that is run.
        """
        self._job = job

    def poll_result(
        self,
    ) -> Tuple[
        Dict[str, List[List[bool]]],
        Dict[str, List[List[float]]],
        Dict[str, List[List[complex]]],
    ]:
        """Poll the result.

        Returns:
            Tuple[Dict[str, List[List[bool]]],
                  Dict[str, List[List[float]]],
                  Dict[str, List[List[complex]]]]: Result if the run was successful.

        Raises:
            RuntimeError: The job failed or was cancelled.
        """
        pass


class QueuedProgramRun:
    """Queued Result of the measurement."""

    def __init__(self, measurement: Any, queued_circuits: List[QueuedCircuitRun]) -> None:
        """Initialise the QueuedProgramRun class.

        Args:
            measurement: the qoqo Measurement to run
            queued_circuits: the list of associated queued circuits
        """
        pass
