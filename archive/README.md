This CHANGELOG includes the old content regarding the packages `qoqo_qiskit_devices` and `roqoqo_qiskit_devices`. Kept for archiving purposes.

# qoqo_qiskit_devices
[![PyPI](https://img.shields.io/pypi/v/qoqo_qiskit_devices)](https://pypi.org/project/qoqo_qiskit_devices/)
[![Documentation Status](https://img.shields.io/badge/docs-documentation-green)](https://hqsquantumsimulations.github.io/qoqo-qiskit/qoqo_qiskit_devices_api/html/index.html)
![Crates.io](https://img.shields.io/crates/l/qoqo-qiskit-devices)

Qiskit devices python interface for the qoqo quantum toolkit by [HQS Quantum Simulations](https://quantumsimulations.de).

In order to make the update a device instance with Qiskit's information possible, the user has to run the following code before using this package:
```python
from qiskit_ibm_provider import IBMProvider

IBMProvider.save_account(token=MY_API_TOKEN)
```
Where `MY_API_TOKEN` is the API key that can be found in the account settings of the IBM Quantum website after registration.

# roqoqo_qiskit_devices
[![Crates.io](https://img.shields.io/crates/v/roqoqo-qiskit-devices)](https://crates.io/crates/roqoqo-qiskit-devices)
![Crates.io](https://img.shields.io/crates/l/roqoqo-qiskit-devices)

Qiskit devices Rust interface for the qoqo quantum toolkit by [HQS Quantum Simulations](https://quantumsimulations.de).

### Installation

To use roqoqo_qiskit_devices in a Rust project simply add

```TOML
roqoqo_qiskit_devices = {version="0.1"}
```

to the `[dependencies]` section of the project Cargo.toml.