# === Turing Machine Simulator ===

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Turing](https://img.shields.io/badge/Machine-Turing-blueviolet)

A simple simulator that allows you to define and run Turing machine programs.

## === Overview ===

This project provides a Python-based Turing machine simulator that executes programs written in a custom notation. The simulator reads a program file that defines symbols and state transitions, then executes the program on an input tape.

## === Getting Started ===

### === Running a Program ===

```bash
python turing.py <program_file>
```

It is recommended that the program file end with .tur, but this is not enforced.

Once the program is finished executing, the tape will be printed.

## === Writing Turing Machine Programs ===

### === Program Structure ===

A Turing machine program consists of three main sections:

1. **Symbol Definition** - Defines the alphabet of symbols used by the machine
2. **State Table** - Defines the states and transitions of the machine
3. **Initial Tape** (optional) - The initial input to the Turing machine

### === Symbols Section ===

The program must begin by defining the set of symbols:

```turing-machine
SYMBOLS
blank_symbol
symbol1
symbol2
...
END
```

Important notes:

- Each symbol must be a single UTF-8 character
- The first symbol is the "blank" symbol (default for empty tape cells)
- Duplicate symbols are ignored
- Comments begin with `;;` and continue to the end of the line

### === State Table ===

After the symbols, define the state table:

```turing-machine
STATE 0
READ <symbol> WRITE <symbol> MOVE <LEFT|RIGHT> NEXT <number|HALT>
...additional instructions...
END

STATE <number>
...instructions...
END

...additional states...
```

### === Initial Tape ===

After the state table, an initial tape can be provided using:

```turing-machine
INITIAL [symbol(s)]
```

Each character after INITIAL is considered a separate "cell" in the tape (excluding whitespace). For example

```turing-machine
INITIAL 10 01 10
```

Will produce an initial tape of [1, 0, 0, 1, 1, 0]

All lines below the initial tape definition (or after the last state table entry if no initial tape is provided) are also ignored.

### === Instructions ===

Each state contains one or more instructions with the following components:

- `READ <symbol>` - If this symbol is under the read/write head, execute this instruction
- `WRITE <symbol>` - Write this symbol to the current cell
- `MOVE <LEFT|RIGHT>` - Move the head one cell left or right
- `NEXT <number|HALT>` - Transition to another state or halt the machine

### === Rules and Requirements ===

- `STATE 0` must be the first state defined (serves as the initial state)
- All symbols used must be defined in the symbols section
- All states referenced in `NEXT` must be defined
- Movement direction must be either `LEFT` or `RIGHT`
- All keywords are case-sensitive (must be uppercase)
- When `HALT` is reached, the final tape will be displayed

### === Warnings ===

The program will issue warnings (but continue execution) for:

- Conflicting instructions: If multiple instructions in the same state have the same `READ` symbol, only the first one will be used
- Multiple definitions of the same state (they will be combined)

### === Errors ===

The program will stop with an error for:

- Missing `STATE 0`
- Invalid symbols in `READ` or `WRITE` instructions
- Invalid move direction
- Jumping to an undefined state
- Invalid syntax

## === Example ===

```turing-machine
SYMBOLS
_ ;; blank symbol
0
1
END

STATE 0
READ _ WRITE 1 MOVE RIGHT NEXT 1
READ 0 WRITE 1 MOVE RIGHT NEXT 1
READ 1 WRITE 1 MOVE LEFT NEXT HALT
END

STATE 1
READ _ WRITE 0 MOVE LEFT NEXT 0
READ 0 WRITE 1 MOVE LEFT NEXT 0
READ 1 WRITE 0 MOVE RIGHT NEXT HALT
END
```

Also see [even_checker.tur](even_checker.tur) for a program that checks if a number is even or odd
