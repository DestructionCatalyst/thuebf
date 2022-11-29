import sys


def find_brackets(program):
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


def interpret(program, memory_size=30000, in_stream=sys.stdin, out_stream=sys.stdout):
    mem = bytearray(memory_size)
    ip = 0  # Instruction pointer
    mp = 0  # Memory pointer
    closing, opening = find_brackets(program)
    while ip < len(program):
        op = program[ip]
        if op == '>':
            if mp == memory_size:
                raise MemoryError("Brainfuck VM out of memory")
            mp += 1
        elif op == '<':
            if mp == 0:
                raise IndexError("Memory pointer out of bounds")
            mp -= 1
        elif op == '+':
            mem[mp] = (mem[mp] + 1) % 256
        elif op == '-':
            mem[mp] = (mem[mp] - 1) % 256
        elif op == '.':
            out_stream.write(chr(mem[mp]))
        elif op == ',':
            input_ = in_stream.read(1)
            if input_:
                mem[mp] = ord(input_)
        elif op == '[':
            if not mem[mp]:
                ip = closing[ip]
        elif op == ']':
            if mem[mp]:
                ip = opening[ip]
        else:
            pass
        ip += 1

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
        # TODO make it configurable whether to load the program into the memory
        program = f.read()
    if args.input == sys.stdin:
        in_file = args.input
    else:
        in_file = open(args.input)
    try:
        interpret(program, memory_size=args.memory, in_stream=in_file)
    finally:
        in_file.close()

