from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, Iterable

from n2t.core.assembler import Assembler


@dataclass
class Executor:
    A_BIT_LOC: int = 3
    COMP_BITS_START: int = 4
    COMP_BITS_END: int = 10
    DEST_BITS_START: int = 10
    DEST_BITS_END: int = 13
    JMP_BITS_START: int = 13
    JMP_BITS_END: int = 16

    MASK: int = 0xFFFF

    # if user doesn't use --cycles option, by default cycles will be -1
    CYCLES_DEFAULT_VALUE: int = -1

    value_of_A: int = 0
    value_of_D: int = 0
    ram_dict: Dict[str, int] = field(default_factory=dict)

    @classmethod
    def create(cls) -> Executor:
        return cls()

    def execute(
        self, file: Iterable[str], cycles: int, is_asm: bool, filepath: str
    ) -> None:
        if is_asm:
            assembler = Assembler.create()
            file = assembler.assemble(file)

        instructions: list[str] = list(file)
        pc: int = 0
        while pc < len(instructions) and cycles != 0:
            instruction: str = instructions[pc]
            if self.is_A_instruction(instruction):
                self.value_of_A = int(instruction, 2)
                pc += 1
            else:
                comp_res: int = self.get_computation_result(instruction)
                self.assign_to_dest(instruction, comp_res)
                pc = self.get_pc_value(instruction, pc, comp_res)
            if cycles != self.CYCLES_DEFAULT_VALUE:
                cycles -= 1

        self.create_json_file(filepath)

    def create_json_file(self, filepath: str) -> None:
        sorted_map = {int(key): value for key, value in self.ram_dict.items()}
        sorted_map = dict(sorted(sorted_map.items()))
        json_object = {"RAM": sorted_map}
        filename, extension = os.path.splitext(filepath)
        json_filename = filename + ".json"

        with open(json_filename, "w") as out_file:
            json.dump(json_object, out_file, indent=4)

    def is_A_instruction(self, instruction: str) -> bool:
        return instruction[0] == "0"

    def a_bit_set(self, instruction: str) -> bool:
        return instruction[self.A_BIT_LOC] == "1"

    def get_comp_bits(self, instruction: str) -> str:
        return instruction[slice(self.COMP_BITS_START, self.COMP_BITS_END)]

    def get_computation_result(self, instruction: str) -> int:
        comp_res: int = 0
        if self.a_bit_set(instruction):
            value_of_M: int = 0
            if str(self.value_of_A) in self.ram_dict:
                value_of_M = self.ram_dict[str(self.value_of_A)]
            comp_res = self.alu(self.get_comp_bits(instruction), value_of_M)
        else:
            copy_of_A: int = self.value_of_A
            comp_res = self.alu(self.get_comp_bits(instruction), copy_of_A)
        return comp_res

    def get_dest_bits(self, instruction: str) -> str:
        return instruction[slice(self.DEST_BITS_START, self.DEST_BITS_END)]

    def assign_to_dest(self, instruction: str, comp_val: int) -> None:
        dest_bits: str = self.get_dest_bits(instruction)
        if dest_bits[2] == "1":
            self.ram_dict[str(self.value_of_A)] = comp_val
        if dest_bits[1] == "1":
            self.value_of_D = comp_val
        if dest_bits[0] == "1":
            self.value_of_A = comp_val

    def get_jmp_bits(self, instruction: str) -> str:
        return instruction[slice(self.JMP_BITS_START, self.JMP_BITS_END)]

    def get_pc_value(self, instruction: str, pc: int, comp_val: int) -> int:
        jmp_bits: str = self.get_jmp_bits(instruction)
        if self.should_jump(jmp_bits, comp_val):
            return self.value_of_A
        else:
            return pc + 1

    def should_jump(self, jmp_bits: str, comp_val: int) -> bool:
        return (
            jmp_bits == "111"
            or (jmp_bits == "001" and comp_val > 0 and not self.is_negative(comp_val))
            or (jmp_bits == "010" and comp_val == 0)
            or (jmp_bits == "011" and not self.is_negative(comp_val))
            or (jmp_bits == "100" and self.is_negative(comp_val))
            or (jmp_bits == "101" and comp_val != 0)
            or (jmp_bits == "110" and (self.is_negative(comp_val) or comp_val == 0))
        )

    def is_negative(self, number: int) -> bool:
        result: int = number & 0x8000
        return result != 0

    def alu(self, comp_bits: str, register_value: int) -> int:
        out: int = 0
        copy_of_D: int = self.value_of_D
        if comp_bits[0] == "1":
            copy_of_D = 0
        if comp_bits[1] == "1":
            copy_of_D = ~copy_of_D & self.MASK
        if comp_bits[2] == "1":
            register_value = 0
        if comp_bits[3] == "1":
            register_value = ~register_value & self.MASK
        if comp_bits[4] == "1":
            out = (copy_of_D + register_value) & self.MASK
        if comp_bits[4] == "0":
            out = (copy_of_D & register_value) & self.MASK
        if comp_bits[5] == "1":
            out = ~out & self.MASK

        return out
