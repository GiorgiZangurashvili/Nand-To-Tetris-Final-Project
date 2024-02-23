from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class Assembler:
    SCREEN: int = 16384
    KBD: int = 24576
    STR_FORMATTER: str = "015b"
    START_OF_A_INSTRUCTION: str = "0"
    START_OF_C_INSTRUCTION: str = "111"

    new_var_value: int = 16

    symbol_table = {
        "R0": 0,
        "R1": 1,
        "R2": 2,
        "R3": 3,
        "R4": 4,
        "R5": 5,
        "R6": 6,
        "R7": 7,
        "R8": 8,
        "R9": 9,
        "R10": 10,
        "R11": 11,
        "R12": 12,
        "R13": 13,
        "R14": 14,
        "R15": 15,
        "SCREEN": SCREEN,
        "KBD": KBD,
        "SP": 0,
        "LCL": 1,
        "ARG": 2,
        "THIS": 3,
        "THAT": 4,
    }

    dest_table = {
        "": "000",
        "M=": "001",
        "D=": "010",
        "MD=": "011",
        "A=": "100",
        "AM=": "101",
        "AD=": "110",
        "AMD=": "111",
    }

    comp_table = {
        "0": "0101010",
        "1": "0111111",
        "-1": "0111010",
        "D": "0001100",
        "A": "0110000",
        "M": "1110000",
        "!D": "0001101",
        "!A": "0110001",
        "!M": "1110001",
        "-D": "0001111",
        "-A": "0110011",
        "-M": "1110011",
        "D+1": "0011111",
        "A+1": "0110111",
        "M+1": "1110111",
        "D-1": "0001110",
        "A-1": "0110010",
        "M-1": "1110010",
        "D+A": "0000010",
        "D+M": "1000010",
        "D-A": "0010011",
        "A-D": "0000111",
        "D-M": "1010011",
        "M-D": "1000111",
        "D&A": "0000000",
        "D&M": "1000000",
        "D|A": "0010101",
        "D|M": "1010101",
    }

    jmp_table = {
        "": "000",
        ";JGT": "001",
        ";JEQ": "010",
        ";JGE": "011",
        ";JLT": "100",
        ";JNE": "101",
        ";JLE": "110",
        ";JMP": "111",
    }

    @classmethod
    def create(cls) -> Assembler:
        return cls()

    def assemble(self, assembly: Iterable[str]) -> Iterable[str]:
        # TODO: your work for Project 6 starts here
        self.get_labels(assembly)
        for instruction in assembly:
            instruction = self.strip_and_remove_comment(instruction)
            if (
                self.is_label(instruction)
                or self.is_comment(instruction)
                or self.is_whitespace(instruction)
            ):
                continue
            yield self.assemble_one(instruction)

    def get_labels(self, assembly: Iterable[str]) -> None:
        label_value: int = 0
        for instruction in assembly:
            instruction = self.strip_and_remove_comment(instruction)
            if self.is_comment(instruction) or self.is_whitespace(instruction):
                continue
            if self.is_label(instruction):
                label: str = instruction.strip("()")
                self.symbol_table[label] = label_value
                continue
            label_value += 1

    def strip_and_remove_comment(self, instruction: str) -> str:
        instruction = instruction.strip()
        return instruction.split("//")[0].strip()

    def is_label(self, instruction: str) -> bool:
        return instruction.find("(") == 0

    def is_comment(self, instruction: str) -> bool:
        return instruction.find("//") == 0

    def is_whitespace(self, instruction: str) -> bool:
        return len(instruction) == 0

    def assemble_one(self, instruction: str) -> str:
        if self.is_address(instruction):
            return self.handle_address(instruction)
        else:
            return self.handle_command(instruction)

    def is_address(self, instruction: str) -> bool:
        return instruction.find("@") == 0

    def handle_command(self, instruction: str) -> str:
        result: str = self.START_OF_C_INSTRUCTION
        result += self.get_comp_bits(instruction)
        result += self.get_dest_bits(instruction)
        result += self.get_jmp_bits(instruction)
        return result

    def handle_address(self, instruction: str) -> str:
        result: str = self.START_OF_A_INSTRUCTION
        key: str = self.get_key(instruction)
        if key.isdigit():
            return result + format(int(key), self.STR_FORMATTER)

        if key not in self.symbol_table:
            self.symbol_table[key] = self.new_var_value
            self.new_var_value += 1
        return result + format(self.symbol_table[key], self.STR_FORMATTER)

    def get_key(self, instruction: str) -> str:
        start: int = instruction.find("@") + 1
        end: int = len(instruction)
        return instruction[start:end]

    def get_comp_bits(self, instruction: str) -> str:
        start: int = self.get_start_index_for_comp(instruction)
        end: int = self.get_end_index_for_comp(instruction)
        key: str = instruction[start:end]
        return self.comp_table[key]

    def get_start_index_for_comp(self, instruction: str) -> int:
        equals_index: int = instruction.find("=")
        if equals_index == -1:
            return 0
        else:
            return equals_index + 1

    def get_end_index_for_comp(self, instruction: str) -> int:
        semicolon_index: int = instruction.find(";")
        if semicolon_index != -1:
            return semicolon_index
        else:
            return len(instruction)

    def get_dest_bits(self, instruction: str) -> str:
        if instruction.find("=") == -1:
            return self.dest_table[""]
        end: int = instruction.find("=") + 1
        key: str = instruction[0:end]
        return self.dest_table[key]

    def get_jmp_bits(self, instruction: str) -> str:
        start: int = instruction.find(";")
        if start == -1:
            return self.jmp_table[""]
        end: int = len(instruction)
        key: str = instruction[start:end]
        return self.jmp_table[key]
