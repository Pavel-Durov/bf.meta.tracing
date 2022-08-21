import os

from rpython.rlib.jit import JitDriver, purefunction
from rpython.jit.codewriter.policy import JitPolicy

def jitpolicy(driver):
    return JitPolicy()


def get_location(pc, program, bracket_map):
    return "%s_%s_%s" % (program[:pc], program[pc], program[pc + 1:])


jitdriver = JitDriver(greens=['pc', 'program', 'bracket_map'], reds=['tape'],
                      get_printable_location=get_location)

OPTIMIZED_BRACKET_MAP=True

def mainloop(program, bracket_map):
    pc = 0
    tape = Tape()

    while pc < len(program):
        jitdriver.jit_merge_point(pc=pc, tape=tape, program=program, bracket_map=bracket_map)
        code = program[pc]

        if code == ">":
            tape.advance()
        elif code == "<":
            tape.devance()
        elif code == "+":
            tape.inc()
        elif code == "-":
            tape.dec()
        elif code == ".":
            os.write(1, chr(tape.get()))
        elif code == ",":
            tape.set(ord(os.read(0, 1)[0]))
        elif code == "[" and tape.get() == 0:
            if OPTIMIZED_BRACKET_MAP:
              pc = get_matching_bracket(bracket_map, pc)
            else:
              pc = bracket_map[pc]
        elif code == "]" and tape.get() != 0:
            if OPTIMIZED_BRACKET_MAP:
              pc = get_matching_bracket(bracket_map, pc)
            else:
              pc = bracket_map[pc]

        pc += 1


class Tape(object):
    def __init__(self):
        self.thetape = [0]
        self.position = 0

    def get(self):
        return self.thetape[self.position]

    def set(self, val):
        self.thetape[self.position] = val

    def inc(self):
        self.thetape[self.position] += 1

    def dec(self):
        self.thetape[self.position] -= 1

    def advance(self):
        self.position += 1
        if len(self.thetape) <= self.position:
            self.thetape.append(0)

    def devance(self):
        self.position -= 1


def parse(program):
    parsed = []
    bracket_map = {}
    leftstack = []

    pc = 0
    for char in program:
        if char in ('[', ']', '<', '>', '+', '-', ',', '.'):
            parsed.append(char)

            if char == '[':
                leftstack.append(pc)
            elif char == ']':
                left = leftstack.pop()
                right = pc
                bracket_map[left] = right
                bracket_map[right] = left
            pc += 1

    return "".join(parsed), bracket_map


@purefunction
def get_matching_bracket(bracket_map, pc):
    return bracket_map[pc]


def run(input):
    program, map = parse(input.read())
    mainloop(program, map)


def run(fp):
    program_contents = ""
    while True:
        read = os.read(fp, 4096)
        if len(read) == 0:
            break
        program_contents += read
    os.close(fp)
    program, bm = parse(program_contents)
    mainloop(program, bm)


def entry_point(argv):
    import os
    try:
        filename = argv[1]
    except IndexError:
        print ("You must supply a filename")
        return 1

    run(os.open(filename, os.O_RDONLY, 0777))
    return 0


def target(*args):
    """
  "target" returns the entry point. 
  The translation process imports your module and looks for that name,
  calls it, and the function object returned is where it starts the translation.
  """
    return entry_point, None


if __name__ == "__main__":
    import sys

    entry_point(sys.argv)
