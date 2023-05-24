"""Test qoqo_qiskit_devices information retrieval"""
# Copyright © 2023 HQS Quantum Simulations GmbH. All Rights Reserved.
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

import pytest
import sys

from qoqo_qiskit_devices import ibm_devices, set_qiskit_noise_information


def test_belem_info_update():
    """Test IBMBelemDevice qiskit's info update."""
    belem = ibm_devices.IBMBelemDevice()
    set_qiskit_noise_information(belem)


if __name__ == "__main__":
    pytest.main(sys.argv)
