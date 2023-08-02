from enum import StrEnum
from collections import defaultdict
import sys
import time
import concurrent.futures

class bf:
    class op(StrEnum):
        PTR_L = '>'
        PTR_R = '<'
        INC = '+'
        DEC = '-'
        OUT = '.'
        IN = ','
        LOOP_O = '['
        LOOP_C = ']'

    def __init__(self, pgrm: str):
        self.tape: dict[int, int] = defaultdict(int)
        self.cell_ptr = 0
        self.pgrm = self.cleanup(pgrm)

    def brackets(self):
        bracket_map = {}
        stack = []
        for i, op in enumerate(self.pgrm):
            if op == self.op.LOOP_O:
                stack.append(i)
            elif op == self.op.LOOP_C:
                s = stack.pop()
                bracket_map[s], bracket_map[i] = i, s
        if stack:
            raise Exception('Unbalanced brackets')
        del stack
        return bracket_map

    def run(self):
        pgrm_ptr = 0
        bracket_map = self.brackets()
        while pgrm_ptr < len(self.pgrm):
            opcode = self.pgrm[pgrm_ptr]
            match opcode:
                case self.op.PTR_L:
                    self.cell_ptr += 1
                case self.op.PTR_R:
                    self.cell_ptr -= 1
                case self.op.INC:
                    self.tape[self.cell_ptr] = (self.tape[self.cell_ptr] + 1) % (256)
                case self.op.DEC:
                    self.tape[self.cell_ptr] = (self.tape[self.cell_ptr] - 1) % (256)
                case self.op.OUT:
                    sys.stdout.write(chr(self.tape[self.cell_ptr]))
                case self.op.IN:
                    self.tape[self.cell_ptr] = ord(input()[0])
                case self.op.LOOP_O:
                    if not self.tape[self.cell_ptr]:
                        pgrm_ptr = bracket_map[pgrm_ptr]
                case self.op.LOOP_C:
                    if self.tape[self.cell_ptr]:
                        pgrm_ptr = bracket_map[pgrm_ptr]
            pgrm_ptr+=1

    def cleanup(self, pgrm: str) -> list[str]:
        return list(filter(lambda x: x in self.op._value2member_map_, pgrm))

if __name__ == '__main__':
    st = time.time()
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            pgrm = f.read()
        c = bf(pgrm)
        max_workers = 12
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(c.run(), range(max_workers))
        print(f"Time: {time.time() - st}")
    else:
        print(f"Usage: {sys.argv[0]} file.bf")