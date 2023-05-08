"""Device information-gathering routines."""
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

from qoqo_qiskit_devices import ibm_devices

from qiskit_ibm_provider import IBMProvider

from typing import Union
import types


class DeviceProperties():
    """Utility for updating the properties on an IBMDevice instance."""

    def __init__(self, device: Union[types.ModuleType, str]) -> None:
        """Initialized DeviceProperty utility.

        Args:
            device (Union[ibm_devices, str]): The qoqo_qiskit_devices instance (or name) that
                is used to get the properties from IBM.

        Raises:
            TypeError: The input is not a string or an `ibm_devices` instance.
        """
        if isinstance(device, str):
            self.properties = IBMProvider().get_backend(device).properties()
        else:
            try:
                self.properties = IBMProvider().get_backend(device.name()).properties()
            except Exception:
                raise TypeError(
                    'The input device is not a string or is not an `ibm_devices` instance.')

    def update(self) -> ibm_devices:
        """Updates the device information.

        Returns:
            ibm_devices: The updated device reference.
        """
        return self.device


if __name__ == '__main__':
    old_dev = ibm_devices.IBMBelemDevice()
    devprop = DeviceProperties(old_dev)
    new_dev = devprop.update()
    print('ciao')
