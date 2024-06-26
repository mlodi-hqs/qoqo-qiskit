# Changelog

This changelog tracks changes of the qoqo_qiskit project starting at version 0.1.0 (initial release).

### 0.6.0

* Updated to pyo3 0.21

### 0.5.0

* Updated to qoqo 1.11
* Simplified the registers representation via dataclasses
* Added `run_circuit_list()` and `run_circuit_list_queued()` allowing to have a single job reference a list of running circuits

### 0.4.2

* Fixed `RotateXY` qiskit equivalence

### 0.4.1

* Fixed overwriting registers bug

### 0.4.0

* Added `run_program()`, `run_program_queued()` allowing for multiple runs in one call thanks to a list of lists of parameter values

### 0.3.0

* Added async support via `QueuedCircuitRun` and `QueuedProgramRun`

### 0.2.5

* Changed function name from `set_qiskit_noise_information` to `set_qiskit_device_information`
* Removed noise information from `set_qiskit_device_information`
* Added `get_noise_models` function

### 0.2.4

* Added support for `PragmaSleep`

### 0.2.3

* Updated to qoqo 1.9
* Added support for Python 3.12
* Pinned qiskit dependency to <0.46
* Added deprecation warnings for retired devices (Lagos, Nairobi, Perth)

### 0.2.2

* Updated qoqo_qiskit_devices `get_decoherence_on_gate_model` method docstring

### 0.2.1

* Updated to qoqo 1.8
* Updated to Pyo3 0.20

### 0.2.0

* Added `get_decoherence_on_gate_model` function.
* Updated to qoqo 1.7
* Added deprecation warnings for retired devices (Belem, Jakarta, Lima, Manila, Quito)
* Added `Identity` gate error info retrieval

### 0.1.10

* Fixed linux deploy issues
* Updated to qoqo 1.6

### 0.1.9

* Corrected `0.1.8` release issues
* Fixed README
* Fixed docs

### 0.1.8

* Added `qoqo_qiskit_device_from_ibmq_identifier` function
* Added warning in case the dephasing obtained from IBM's machines turns out to be negative

### 0.1.7

* Fixed missing transformation of T2 to Tphi

### 0.1.6

* Added `to_generic_device` method

### 0.1.5

* Updated to qoqo 1.5
* Updated to pyo3 0.19

### 0.1.4

* Added qoqo_qiskit_devices and roqoqo_qiskit_devices to the repository

### 0.1.3

* Correcting Github release issues

### 0.1.2

* Added support for `PragmaLoop`

### 0.1.1

* Corrects initial release

### 0.1.0

* Initial release
