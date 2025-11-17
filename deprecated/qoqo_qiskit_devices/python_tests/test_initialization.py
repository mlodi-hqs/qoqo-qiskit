"""Test qoqo_qiskit_devices initialization"""

# Copyright © 2023-2025 HQS Quantum Simulations GmbH. All Rights Reserved.
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

import warnings
import pytest
import sys

from qoqo_qiskit_devices import ibm_devices


def test_belem():
    """Test IBMBelemDevice initialization."""
    with warnings.catch_warnings(record=True) as w:
        dev = ibm_devices.IBMBelemDevice()
        assert len(w) == 1
        assert issubclass(w[-1].category, DeprecationWarning)
        assert "retired" in str(w[-1].message)
        assert dev.name() in str(w[-1].message)


def test_jakarta():
    """Test IBMJakartaDevice initialization."""
    with warnings.catch_warnings(record=True) as w:
        dev = ibm_devices.IBMJakartaDevice()
        assert len(w) == 1
        assert issubclass(w[-1].category, DeprecationWarning)
        assert "retired" in str(w[-1].message)
        assert dev.name() in str(w[-1].message)


def test_lagos():
    """Test IBMLagosDevice initialization."""
    with warnings.catch_warnings(record=True) as w:
        dev = ibm_devices.IBMLagosDevice()
        assert len(w) == 1
        assert issubclass(w[-1].category, DeprecationWarning)
        assert "retired" in str(w[-1].message)
        assert dev.name() in str(w[-1].message)


def test_lima():
    """Test IBMLimaDevice initialization."""
    with warnings.catch_warnings(record=True) as w:
        dev = ibm_devices.IBMLimaDevice()
        assert len(w) == 1
        assert issubclass(w[-1].category, DeprecationWarning)
        assert "retired" in str(w[-1].message)
        assert dev.name() in str(w[-1].message)


def test_manila():
    """Test IBMManilaDevice initialization."""
    with warnings.catch_warnings(record=True) as w:
        dev = ibm_devices.IBMManilaDevice()
        assert len(w) == 1
        assert issubclass(w[-1].category, DeprecationWarning)
        assert "retired" in str(w[-1].message)
        assert dev.name() in str(w[-1].message)


def test_nairobi():
    """Test IBMNairobiDevice initialization."""
    with warnings.catch_warnings(record=True) as w:
        dev = ibm_devices.IBMNairobiDevice()
        assert len(w) == 1
        assert issubclass(w[-1].category, DeprecationWarning)
        assert "retired" in str(w[-1].message)
        assert dev.name() in str(w[-1].message)


def test_perth():
    """Test IBMPerthDevice initialization."""
    with warnings.catch_warnings(record=True) as w:
        dev = ibm_devices.IBMPerthDevice()
        assert len(w) == 1
        assert issubclass(w[-1].category, DeprecationWarning)
        assert "retired" in str(w[-1].message)
        assert dev.name() in str(w[-1].message)


def test_quito():
    """Test IBMQuitoDevice initialization."""
    with warnings.catch_warnings(record=True) as w:
        dev = ibm_devices.IBMQuitoDevice()
        assert len(w) == 1
        assert issubclass(w[-1].category, DeprecationWarning)
        assert "retired" in str(w[-1].message)
        assert dev.name() in str(w[-1].message)


if __name__ == "__main__":
    pytest.main(sys.argv)
