# Copyright © 2024-2025 HQS Quantum Simulations GmbH.
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
"""Results post-processing utilities."""

from dataclasses import astuple
from typing import Dict, List, Optional, Tuple, Union

from qiskit.result import Result
from qoqo import Circuit

from ..models import RegistersWithLengths


def _split(element: str, bit_regs_lengths: Dict[str, int]) -> List[str]:
    splitted: list[str] = []
    if " " in element:
        splitted = element.split()
        splitted.reverse()
    else:
        element = element[::-1]
        for key in bit_regs_lengths:
            splitted.append(element[: bit_regs_lengths[key] :])
            splitted[-1] = splitted[-1][::-1]
            element = element[bit_regs_lengths[key] :]
    return splitted


def _transform_job_result_single(
    _memory: bool,
    sim_type: str,
    result: Result,
    output_register: RegistersWithLengths,
    input_bit_circuit: Optional[Circuit],
    res_index: Optional[int] = 0,
) -> None:
    # res_index is the index of the chosen result to extract in case
    #  the single Result contains multiple ExperimentalResult instances
    if sim_type == "automatic":
        for reg in output_register.registers.bit_register_dict:
            qiskit_counts_dictionary = result[res_index].data[reg].get_counts()
            for qiskit_qubits, count in qiskit_counts_dictionary.items():
                to_bool_list = [char == "1" for char in qiskit_qubits]
                to_bool_list.reverse()
                for _ in range(count):
                    output_register.registers.bit_register_dict[reg].append(to_bool_list)
        if input_bit_circuit:
            for input_bit_op in input_bit_circuit:
                for bit_result in output_register.registers.bit_register_dict[input_bit_op.name()]:
                    bit_result[input_bit_op.index()] = input_bit_op.value()


def _transform_job_result_list(
    memory: bool,
    sim_type: str,
    result: Result,
    output_registers: List[RegistersWithLengths],
    input_bit_circuits: List[Optional[Circuit]],
) -> None:
    if sim_type == "automatic":
        for i, (output_register, input_bit_circuit) in enumerate(
            zip(output_registers, input_bit_circuits)
        ):
            _transform_job_result_single(
                memory, sim_type, result, output_register, input_bit_circuit, i
            )


def _transform_job_result(
    memory: bool,
    sim_type: str,
    result: Result,
    output_registers: Union[RegistersWithLengths, List[RegistersWithLengths]],
    input_bit_circuits: Union[Optional[Circuit], List[Optional[Circuit]]],
    res_index: Optional[int] = 0,
) -> Tuple[
    Dict[str, List[List[bool]]],
    Dict[str, List[List[float]]],
    Dict[str, List[List[complex]]],
]:
    if isinstance(output_registers, list) and isinstance(input_bit_circuits, list):
        _transform_job_result_list(memory, sim_type, result, output_registers, input_bit_circuits)
        final_output = RegistersWithLengths()
        for regs in output_registers:
            for key, value_bools in regs.registers.bit_register_dict.items():
                if key in final_output.registers.bit_register_dict:
                    final_output.registers.bit_register_dict[key].extend(value_bools)
                else:
                    final_output.registers.bit_register_dict[key] = value_bools
            for key, value_floats in regs.registers.float_register_dict.items():
                if key in final_output.registers.float_register_dict:
                    final_output.registers.float_register_dict[key].extend(value_floats)
                else:
                    final_output.registers.float_register_dict[key] = value_floats
            for key, value_complexes in regs.registers.complex_register_dict.items():
                if key in final_output.registers.complex_register_dict:
                    final_output.registers.complex_register_dict[key].extend(value_complexes)
                else:
                    final_output.registers.complex_register_dict[key] = value_complexes
        return astuple(final_output.registers)
    elif isinstance(output_registers, RegistersWithLengths) and (
        isinstance(input_bit_circuits, Circuit) or input_bit_circuits is None
    ):
        _transform_job_result_single(
            memory,
            sim_type,
            result,
            output_registers,
            input_bit_circuits,
            res_index,
        )
        return astuple(output_registers.registers)
    else:
        raise ValueError("Invalid input for output_registers and/or input_bit_circuits.")
