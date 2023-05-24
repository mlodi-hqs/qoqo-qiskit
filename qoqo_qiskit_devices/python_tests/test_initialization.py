"""Test qoqo_qiskit_devices initialization"""
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

from qoqo_qiskit_devices import ibm_devices


def test_belem():
    """Test IBMBelemDevice initialization."""
    belem = ibm_devices.IBMBelemDevice()


def test_jakarta():
    """Test IBMJakartaDevice initialization."""
    jakarta = ibm_devices.IBMJakartaDevice()


def test_lagos():
    """Test IBMLagosDevice initialization."""
    lagos = ibm_devices.IBMLagosDevice()


def test_lima():
    """Test IBMLimaDevice initialization."""
    lima = ibm_devices.IBMLimaDevice()


def test_manila():
    """Test IBMManilaDevice initialization."""
    manila = ibm_devices.IBMManilaDevice()


def test_nairobi():
    """Test IBMNairobiDevice initialization."""
    nairobi = ibm_devices.IBMNairobiDevice()


def test_perth():
    """Test IBMPerthDevice initialization."""
    perth = ibm_devices.IBMPerthDevice()


def test_quito():
    """Test IBMQuitoDevice initialization."""
    quito = ibm_devices.IBMQuitoDevice()


if __name__ == "__main__":
    pytest.main(sys.argv)
