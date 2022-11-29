import sys
import io
from typing import Union, Dict, Tuple

from util import close_if_not_system


def find_brackets(program: str) -> Tuple[Dict[int, int], Dict[int, int]]:
    stack = []
    open_to_close = {}
    close_to_open = {}
    for pos, op in enumerate(program):
        if op == '[':
            stack.append(pos)
        elif op == ']':
            if stack:
                open = stack.pop()
            else:
                raise Exception("Unmatched ]")
            open_to_close[open] = pos
            close_to_open[pos] = open
    if stack:
        raise Exception("Unmatched [")
    return open_to_close, close_to_open


class BrainfuckVirtualMachine:
    def __init__(self, memory_size: int = 30000) -> None:
        self.mem = bytearray(memory_size)
        self.mp = 0  # Memory pointer
        self.ip = None  # Instruction pointer
        self.program = program
        self.closing, self.opening = None, None
        self.in_stream = sys.stdin
        self._in_stream_opened = False
        self.out_stream = sys.stdout
        self._out_stream_opened = False

    def load_program(self, program: str) -> None:
        self.ip = 0  # Instruction pointer
        self.program = program
        self.closing, self.opening = find_brackets(program)

    def set_in_stream(self, file: Union[str, io.TextIOWrapper] = sys.stdin) -> None:
        if self._in_stream_opened:
            close_if_not_system(self.in_stream)
        if not isinstance(file, io.TextIOWrapper):
            self._in_stream_opened = True
            file = open(file)
        else:
            self._in_stream_opened = False
        self.in_stream = file

    def set_out_stream(self, file: Union[str, io.TextIOWrapper] = sys.stdout) -> None:
        if self._out_stream_opened:
            close_if_not_system(self.out_stream)
        if not isinstance(file, io.TextIOWrapper):
            self._out_stream_opened = True
            file = open(file)
        else:
            self._out_stream_opened = False
        self.out_stream = file

    def execute_instruction(self) -> None:
        if self.ip is None:
            raise ValueError("Program is not loaded")
        op = self.program[self.ip]
        if op == '>':
            if self.mp == len(self.mem):
                raise MemoryError("Brainfuck VM out of memory")
            self.mp += 1
        elif op == '<':
            if self.mp == 0:
                raise IndexError("Memory pointer out of bounds")
            self.mp -= 1
        elif op == '+':
            self.mem[self.mp] = (self.mem[self.mp] + 1) % 256
        elif op == '-':
            self.mem[self.mp] = (self.mem[self.mp] - 1) % 256
        elif op == '.':
            self.out_stream.write(chr(self.mem[self.mp]))
        elif op == ',':
            input_ = self.in_stream.read(1)
            if input_:
                self.mem[self.mp] = ord(input_)
        elif op == '[':
            if not self.mem[self.mp]:
                self.ip = self.closing[self.ip]
        elif op == ']':
            if self.mem[self.mp]:
                self.ip = self.opening[self.ip]
        else:
            pass
        self.ip += 1

    def unload_program(self):
        self.ip = None
        self.program = None
        self.closing, self.opening = None, None

    def execute_program(self, program: str) -> None:
        self.load_program(program)
        while self.ip < len(self.program):
            self.execute_instruction()
        self.unload_program()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unload_program()
        if self._in_stream_opened:
            close_if_not_system(self.in_stream)
        if self._out_stream_opened:
            close_if_not_system(self.out_stream)


# TODO debug mode + debugger
# https://stackoverflow.com/questions/24072790/how-to-detect-key-presses
# https://docs.python.org/3/library/curses.html
debug = False


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('code', help='The file with Brainfuck code to interpret')
    parser.add_argument('-i', '--input',
                        help='The file to serve as an input when reading via , command. Defaults to stdin',
                        default=sys.stdin)
    parser.add_argument('-m', '--memory',
                        type=int,
                        help='Memory size of Brainfuck virtual machine. Defaults to 30 000',
                        default=30_000)
    args = parser.parse_args()
    with open(args.code) as f:
        program = f.read()
    with BrainfuckVirtualMachine(args.memory) as bfvm:
        bfvm.set_in_stream(args.input)
        bfvm.execute_program(program)
