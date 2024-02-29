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
"""Backend module utilities."""

import re


def is_valid_uuid4(uuid_to_test: str) -> bool:
    """Check if uuid_to_test is a valid UUID (version4).

    This checks whether a job_id comes from qiskit_aer (so locally executed job)
    or qiskit_runtime.

    Parameters:
        uuid_to_test (str): UUID to validate in string format.

    Returns:
        bool: True if uuid_to_test is valid UUID, else False.
    """
    uuid_regex = (
        r"^[a-fA-F0-9]{8}-"  # 8 hexadecimal characters for the time_low segment
        r"[a-fA-F0-9]{4}-"  # 4 hexadecimal characters for the time_mid segment
        r"4[a-fA-F0-9]{3}-"  # The "4" indicates the UUID version
        r"[89ABab][a-fA-F0-9]{3}-"  # The first character can be 8, 9, A, or B for the variant
        r"[a-fA-F0-9]{12}$"  # 12 hexadecimal characters for the node segment
    )

    match = re.fullmatch(uuid_regex, str(uuid_to_test))
    return bool(match)
