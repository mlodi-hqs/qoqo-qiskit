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
"""Results post-processing utilities."""

from dataclasses import astuple
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from qiskit.result import Result
from qoqo import Circuit

from ..models import RegistersWithLengths


def _counts_to_registers(
    counts: Any, mem: bool, clas_regs_lengths: Dict[str, int]
) -> List[List[List[bool]]]:
    bit_map: List[List[List[bool]]] = []
    reg_num = 0
    for key in clas_regs_lengths:
        reg_num += clas_regs_lengths[key]
    for _ in range(reg_num):
        bit_map.append([])
    for key in counts:
        splitted = _split(key, clas_regs_lengths)
        for i, measurement in enumerate(splitted):
            transf_measurement = _bit_to_bool(measurement)
            if mem:
                bit_map[i].append(transf_measurement)
            else:
                for _ in range(counts[key]):
                    bit_map[i].append(transf_measurement)
    return bit_map


def _are_measurement_operations_in(circuit: Circuit) -> bool:
    for op in circuit:
        if "Measurement" in op.tags():
            return True
    return False


def _bit_to_bool(element: str) -> List[bool]:
    ret = []
    for char in element:
        ret.append(char.lower() in ("1"))
    return ret


def _split(element: str, clas_regs_lengths: Dict[str, int]) -> List[str]:
    splitted: list[str] = []
    if " " in element:
        splitted = element.split()
        splitted.reverse()
    else:
        element = element[::-1]
        for key in clas_regs_lengths:
            splitted.append(element[: clas_regs_lengths[key] :])
            splitted[-1] = splitted[-1][::-1]
            element = element[clas_regs_lengths[key] :]
    return splitted


def _transform_job_result_single(
    memory: bool,
    sim_type: str,
    result: Result,
    output_registers: RegistersWithLengths,
    res_index: Optional[int] = 0,
) -> None:
    # res_index is the index of the chosen result to extract in case
    #  the single Result contains multiple ExperimentalResult instances
    if sim_type == "automatic":
        transformed_counts = _counts_to_registers(
            result.get_memory(res_index) if memory else result.get_counts(res_index),
            memory,
            output_registers.clas_regs_lengths,
        )
        for i, reg in enumerate(output_registers.registers.bit_register_dict):
            output_registers.registers.bit_register_dict[reg] = [
                shot[::-1] for shot in transformed_counts[i]
            ]
    elif sim_type == "statevector":
        vector = list(np.asarray(result.data(res_index)["statevector"]).flatten())
        for reg in output_registers.registers.complex_register_dict:
            output_registers.registers.complex_register_dict[reg].append(vector)
    elif sim_type == "density_matrix":
        vector = list(np.asarray(result.data(res_index)["density_matrix"]).flatten())
        for reg in output_registers.registers.complex_register_dict:
            output_registers.registers.complex_register_dict[reg].append(vector)


def _transform_job_result_list(
    memory: bool,
    sim_type: str,
    result: Result,
    output_registers: List[RegistersWithLengths],
) -> None:
    if sim_type == "automatic":
        res_list = result.get_memory() if memory else result.get_counts()
        for res, regs in zip(res_list, output_registers):
            transformed_counts = _counts_to_registers(res, memory, regs.clas_regs_lengths)
            for i, reg in enumerate(regs.registers.bit_register_dict):
                regs.registers.bit_register_dict[reg] = [
                    shot[::-1] for shot in transformed_counts[i]
                ]
    elif sim_type == "statevector":
        for i, regs in enumerate(output_registers):
            vector = list(np.asarray(result.data(i)["statevector"]).flatten())
            for reg in regs.registers.complex_register_dict:
                regs.registers.complex_register_dict[reg].append(vector)
    elif sim_type == "density_matrix":
        for i, regs in enumerate(output_registers):
            vector = list(np.asarray(result.data(i)["density_matrix"]).flatten())
            for reg in regs.registers.complex_register_dict:
                regs.registers.complex_register_dict[reg].append(vector)


def _transform_job_result(
    memory: bool,
    sim_type: str,
    result: Result,
    output_registers: Union[RegistersWithLengths, List[RegistersWithLengths]],
    res_index: Optional[int] = 0,
) -> Tuple[
    Dict[str, List[List[bool]]],
    Dict[str, List[List[float]]],
    Dict[str, List[List[complex]]],
]:
    if isinstance(output_registers, list):
        _transform_job_result_list(memory, sim_type, result, output_registers)
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
    else:
        _transform_job_result_single(memory, sim_type, result, output_registers, res_index)
        return astuple(output_registers.registers)
