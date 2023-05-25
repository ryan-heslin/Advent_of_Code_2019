from copy import deepcopy
from typing import Generator
from typing import List
from typing import Union

import utils.intcode as ic
from utils.utils import split_commas


# Output values are appended as written, so this should be okay
def output(program, value):
    # 3 output vals mean complete packet, so send to common queue
    program.write(value)
    if len(program.private_output) == 3:
        program.common_output.extend(program.private_output)
        program.clear()
    return -1


# Monkey-patch modified write operation
output_code = 4
operations = deepcopy(ic.operations)
operations[output_code] = ic.Operation(output_code, 1, output, False)


class NetworkedProgram(ic.Program):
    def __init__(self, common_output, **kwargs):
        super().__init__(**kwargs)
        self.operations = operations
        self.private_output = []
        self.common_output = common_output

    def write(self, value):
        self.private_output.append(value)

    def clear(self):
        self.private_output = []

    @property
    def output(self):
        return list(self.private_output)


def run_network(code, size=50):
    default = (-1,)
    shared_queue = []
    programs: List[Union["NetworkedProgram", None]] = [None] * size
    instances: List[Union[Generator, None]] = [None] * size

    for i in range(size):
        programs[i] = NetworkedProgram(
            code=dict(code), input=(i,), common_output=shared_queue
        )
        instances[i] = programs[i].eval(False)
        next(instances[i])
        instances[i].send(default)

    part1 = NAT_packet = last_y = None
    end_val = 255

    while True:
        while shared_queue:
            if len(shared_queue) < 3:
                break
            target = shared_queue[0]
            data = shared_queue[1:3]

            if target == end_val:
                if part1 is None:
                    part1 = data[1]
                NAT_packet = data
            else:
                instances[target].send(data)
            del shared_queue[:3]

        instances[0].send(NAT_packet)
        if NAT_packet[-1] == last_y:
            return part1, last_y
        last_y = NAT_packet[-1]
        NAT_packet = None


code = ic.Program.parse(split_commas("inputs/day23.txt"))
part1, part2 = run_network(code)
print(part1)
print(part2)
