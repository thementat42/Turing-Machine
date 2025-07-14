

import sys
from typing import Any


LEFT = -1
RIGHT = 1
READ = "READ"
WRITE = "WRITE"
MOVE = "MOVE"
NEXT = "NEXT"
END = "END"
HALT = "HALT"
STATE = "STATE"
INITIAL = "INITIAL"

class TuringMachineError(Exception):
    pass

class Instruction:
    def __init__(self, read_symbol: str, write_symbol: str, move: int, next: int|None = None) -> None:
        self.read = read_symbol
        self.write = write_symbol
        self.move = move
        self.next = next
    
    def __repr__(self) -> str:
        return f"READ {self.read} WRITE {self.write} MOVE {"LEFT" if self.move == LEFT else "RIGHT"} NEXT {self.next if self.next is not None else HALT}"

    def __eq__(self, other: Any):
        if not isinstance(other, Instruction):
            return False
        # Only compare read attributes
        return self.read == other.read
    
    def __hash__(self):
        # Hash based only on read symbol
        return hash(self.read)

def get_lines(filename: str):
    processed: list[str] = []
    with open(filename, 'r', encoding = "utf8") as f:
        while (line := f.readline()):
            try:
                comment = line.index(";;")
                l = line[:comment].strip().rstrip('\n')
                if l: processed.append(l)
            except ValueError:
                # No comment
                l = line.rstrip('\n')
                if l: processed.append(l)
    return processed

def get_symbols(lines: list[str]):
    symbols: list[str] = []
    if (lines[0] != "SYMBOLS"):
        raise TuringMachineError("File should start with 'SYMBOLS'")
    i = 1
    while (i < len(lines) and lines[i] != END):
        if (lines[i] in symbols):
            print(f"Warning: duplicate symbol {lines[i]}")
        if len(lines[i]) != 1:
            raise TuringMachineError(f"Symbols should be 1 character long (line {i})")
        symbols.append(lines[i])
        i += 1
    if i >= len(lines):
        raise TuringMachineError(f"Expected 'END' to end the SYMBOLS block (line {i})")
    if not symbols:
        raise TuringMachineError("Empty symbols list")
    return set(symbols), i + 1, symbols[0]  # + 1 to skip "END"

def make_instruction(line: str, line_number: int, symbols: set[str]):
    instructions = line.split(' ')

    # Check that the instructions list matches the expected format
    if len(instructions) != 8:
        raise TuringMachineError(f"Instructions should look like '{READ} [symbol] {WRITE} [symbol] {MOVE} [LEFT|RIGHT] {NEXT} [number|{HALT}]' (line {line_number})")
    if instructions[0] != READ or instructions[2] != WRITE or instructions[4] != MOVE or instructions[6] != NEXT:
        raise TuringMachineError(f"Instructions should look like 'READ [symbol] WRITE [symbol] MOVE [LEFT|RIGHT] NEXT [number|HALT]' (line {line_number})")
    
    # Verify that the instruction is valid:
    #   Reading a valid symbol
    #   Writing a valid symbol
    #   Moving in a valid direction
    #   The next state is an integer
    if instructions[1] not in symbols:
        raise TuringMachineError(f"'{instructions[1]}' was not a valid symbol to read (line {line_number})")

    if instructions[3] not in symbols:
        raise TuringMachineError(f"'{instructions[3]}' was not a valid symbol to write (line {line_number})")
    
    if instructions[5] not in ("LEFT", "RIGHT"):
        raise TuringMachineError(f"'{instructions[5]}' was not a valid direction (line {line_number})")

    if not instructions[7].isdigit() and instructions[7] != HALT:
        raise TuringMachineError(f"The next state should be a number, or {HALT}, not '{instructions[7]}' (line {line_number})")

    return Instruction(
        read_symbol=instructions[1], 
        write_symbol=instructions[3], 
        move = (LEFT if instructions[5] == "LEFT" else RIGHT),
        next = (None if instructions[7] == HALT else int(instructions[7])))
    

def make_state_table(lines: list[str], start_line: int, symbols: set[str]):
    if (start_line >= len(lines)):
        raise TuringMachineError("No instructions")
    if (lines[start_line] != "STATE 0"):
        raise TuringMachineError(f"States should start with STATE 0, not {lines[start_line]}")
    i = start_line + 1

    program: dict[int, set[Instruction]] = {}
    state_0_instructions: set[Instruction] = set()
    while (i < len(lines) and lines[i] != END):
        new_instruction = make_instruction(lines[i], i, symbols)
        if new_instruction in state_0_instructions:
            print(f"Warning: an instruction with a read directive of {new_instruction.read} was already defined for state 0 (redefinition on line {i})")
        else:
            state_0_instructions.add(new_instruction)
        i += 1
    if i >= len(lines):
        raise TuringMachineError(f"Expected 'END' to end the state 0 block (line {i})")
    program[0] = state_0_instructions
    i += 1

    while (i < len(lines) and lines[i].startswith(STATE)):
        state_number = lines[i].split(STATE)[1].strip()
        if not state_number.isdigit():
            raise TuringMachineError(f"States should have a number, not {state_number} (line {i})") from ValueError
        state_number = int(state_number)
        i += 1
        instructions: set[Instruction] = set()
        while (i < len(lines) and lines[i] != "END"):
            instructions.add(make_instruction(lines[i], i, symbols))
            i += 1
        if lines[i] != "END":
            raise TuringMachineError(f"Expected 'END' to end the block for state {state_number} (line {i})")
        if state_number in program.keys():
            print(f"Warning: {state_number} is already a state (redeclaration on line {i} will be extended to include further declarations)")
            program[state_number].update(instructions)
        else:
            program[state_number] = instructions
        i += 1
    return program, i

def get_initial_tape(lines: list[str], start_line: int, symbols: set[str], blank: str):
    if start_line >= len(lines):
        print("Warning: no initial tape given. Defaulting to a tape of all blanks")
        return [blank]
    if not (lines[start_line].startswith(INITIAL)):
        raise TuringMachineError("Expected 'INITIAL' for an initial tape")
    initial_tape = "".join(lines[start_line].split(INITIAL)[1:])
    initial_tape = [i for i in initial_tape if i != ' ']  # Skip whitespace and INITIAL
    if len(initial_tape) == 0:
        print("Warning: no initial tape given. Defaulting to a tape of all blanks")
        return [blank]
    
    # Verify all symbols in the initial tape are valid
    if not all(sym in symbols for sym in initial_tape):
        invalid = [sym for sym in initial_tape if sym not in symbols]
        raise TuringMachineError(f"Invalid symbol(s) {invalid} in initial tape")

    return initial_tape
    

def interpret(filename: str):
    lines = get_lines(filename)
    symbols, i, blank = get_symbols(lines)
    state_table, i = make_state_table(lines, i, symbols)
    initial_tape = get_initial_tape(lines, i, symbols, blank)

    left_edge = 0
    right_edge = 0
    tape: dict[int, str] = {}
    head = 0

    for idx, sym in enumerate(initial_tape):
        tape[idx] = sym
    # Update right edge to account for initial tape length
    right_edge = max(right_edge, len(initial_tape) - 1)

    current_state = 0
    done = False
    while not done:
        try:
            instructions = state_table[current_state]
        except KeyError as e:
            raise TuringMachineError(f"{current_state} is not a defined state") from e
        for instruction in instructions:
            if tape[head] == instruction.read:
                tape[head] = instruction.write
                head += instruction.move

                left_edge = min(left_edge, head)
                right_edge = max(right_edge, head)
                if head not in tape:
                    tape[head] = blank

                if instruction.next is None:
                    done = True
                else:
                    current_state = instruction.next
                break
        else:  # didn't break
            raise TuringMachineError(f"State {current_state} did not have a READ instruction for the symbol {tape[head]}")
    
    print("Final tape:")
    for pos in range(left_edge, right_edge + 1):
        print(tape.get(pos, blank), end = " ")
    print()

def main():
    if len(sys.argv) < 2:
        print("Usage: python [filename]")
        return 1
    filename = sys.argv[1]
    interpret(filename)
    return 0

if __name__ == "__main__":
    main()