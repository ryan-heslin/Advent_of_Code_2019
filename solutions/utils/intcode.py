from collections import defaultdict
from enum import Enum


class Exit(Enum):
    COMPLETE = 0  # program finished
    OUTPUT = 1  # exiting on output write
    INPUT = 2  # input exhausted, exiting to read input


def identity(x, *_):
    return x


# write: is last param always a code index to write to?
class Operation:
    def __init__(self, code, n_params, operation, write=True):
        self.__code = code
        self.__n_params = n_params
        self.__operation = operation
        self.write = write

    @property
    def code(self):
        return self.__code

    @property
    def n_params(self):
        return self.__n_params

    @property
    def operation(self):
        return self.__operation


class ParamCode:
    def __init__(self, code, literal_code, substitute):
        self.__code = code
        self.__literal_code = literal_code
        self.substitute = substitute

    @property
    def code(self):
        return self.__code

    @property
    def literal_code(self):
        return self.__literal_code


# Define behavior for all parameter codes
param_codes = (
    ParamCode(0, 1, lambda param, program: program.code[param]),
    ParamCode(1, 1, identity),
    ParamCode(2, 3, lambda param, program: program.code[param + program.relative_base]),
    ParamCode(3, 3, lambda param, program: param + program.relative_base),
)
param_codes = {obj.code: obj for obj in param_codes}


# Write parameters never in immediate mode
def _add(program, x, y, pos):
    program[pos] = x + y


def _mul(program, x, y, pos):
    program[pos] = x * y


def __input(program, position):
    value = program.read()
    program[position] = value


def _output(program, value):
    program.write(value)
    return -1


def _jump_if_true(_, x, y):
    return y if x != 0 else None


def _jump_if_false(_, x, y):
    return y if x == 0 else None


def _less_than(program, x, y, position):
    program[position] = int(x < y)


def _equal_to(program, x, y, position):
    program[position] = int(x == y)


def _adjust_rel(program, x):
    program.relative_base += x


# See https://www.reddit.com/r/adventofcode/comments/e8aw9j/2019_day_9_part_1_how_to_fix_203_error/
# This is the default mode. For special cases, there is literal mode:
#
#     Mode 0 and 1 resolve to raw
#     Mode 2 resolves to relative_base + raw
#
# When to use literal mode?
#
#     When resolving the third parameter for writes, for example opcodes 1, 2, 7, 8...
#
#     When resolving the first parameter for writes, for example opcode 3 (this is the 203 error)
operations = [
    Operation(1, 3, _add, True),
    Operation(2, 3, _mul, True),
    Operation(99, 0, lambda *args: None, False),
    Operation(3, 1, __input, True),
    Operation(4, 1, _output, False),
    Operation(5, 2, _jump_if_true, False),
    Operation(6, 2, _jump_if_false, False),
    Operation(7, 3, _less_than, True),
    Operation(8, 3, _equal_to, True),
    Operation(9, 1, _adjust_rel, False),
]
operations = {op.code: op for op in operations}


class Program:

    __param_codes = param_codes

    def __init__(
        self, code: dict[int, int], halt_code=99, input=None, operations=operations
    ):
        self.__code = defaultdict(lambda: 0)
        self.__code.update(dict(code))
        self.__halt_code = halt_code
        if input is None:
            self.__input = []
        else:
            self.__input = list(input)
        self.__output = []
        self.__position = self.relative_base = 0
        self.operations = operations

    def modify(self, replacements: dict[int, int]):
        l = len(self)
        if not (0 <= min(replacements.values()) < l) and (
            0 <= max(replacements.values()) < l
        ):
            raise ValueError("Invalid replacement index")
        for idx, val in replacements.items():
            self.__code[idx] = val
        return self

    def write(self, value):
        self.__output.append(value)

    # Read from input
    def read(self):
        return self.__input.pop(0)

    def eval(self, yield_on_output=False):
        cls = type(self)

        while True:
            raw_opcode = self.__code[self.__position]
            opcode, param_codes = self.read_opcode(raw_opcode)
            # KeyError here means unsupported operation
            operation = self.operations[opcode]

            if operation.code == self.__halt_code:
                yield Exit.COMPLETE

            # +1 to account for opcode
            consumed = operation.n_params + 1
            raw_params = (
                self.__code[i]
                for i in range(self.__position + 1, self.__position + consumed)
            )
            # For last opcode, "position mode" means "overwrite whatever value is at this position"
            # Input takes value directly from position
            final_params = self.prepare_params(raw_params, param_codes)

            # Halt to read input if none available
            if operation.code == 3 and not len(self.__input):
                new = yield Exit.INPUT
                self.update(values=new)

            result = operation.operation(self, *final_params)

            # TODO clean this up
            self.__position = (
                result
                if result is not None and result != -1
                else self.__position + consumed
            )
            # Exit on output
            if yield_on_output and result == -1:
                yield Exit.OUTPUT

    # Convert opcode number to opcode and param type codes
    def read_opcode(self, code):
        opcode = code % 100
        code //= 100

        n_params = self.operations[opcode].n_params
        param_codes = [None] * n_params

        for i in range(n_params):
            this_code = code % 10
            param_codes[i] = this_code
            code //= 10
        if self.operations[opcode].write:
            param_codes[-1] = self.__param_codes[param_codes[-1]].literal_code

        return opcode, param_codes

    # Convert indices to values for params with appropriate type
    def prepare_params(self, raw_params, param_codes):
        return [
            self.__param_codes[param_code].substitute(param, self)
            for param, param_code in zip(raw_params, param_codes, strict=True)
        ]

    def run_to_exhaustion(self):
        gen = self.eval()
        while True:
            result = next(gen)
            if result == Exit.COMPLETE:
                yield self
            elif result == Exit.INPUT:
                new = yield
                gen.send(new)

    # Add more input
    def update(self, values):
        self.__input.extend(values)

    def clear(self):
        self.__output = []

    def __len__(self):
        return len(self.__code)

    def __setitem__(self, key, value):
        self.__code[key] = value

    @property
    def code(self):
        return self.__code

    @staticmethod
    def parse(nums):
        return {i: int(x) for i, x in enumerate(nums)}

    @property
    def output(self):
        return list(self.__output)
