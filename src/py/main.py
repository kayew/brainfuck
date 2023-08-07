import sys
import time
from collections import defaultdict

class bf:
    def __init__(self, pgrm: str):
        self.tape: dict[int, int] = defaultdict(int)
        self.cell_ptr = 0
        self.pgrm = self.cleanup(pgrm)

    def brackets(self):
        bracket_map = {}
        stack = []
        for i, op in enumerate(self.pgrm):
            if op == "[":
                stack.append(i)
            elif op == "]":
                s = stack.pop()
                bracket_map[s], bracket_map[i] = i, s
        if stack:
            raise Exception("Unbalanced brackets")
        del stack
        return bracket_map

    def run(self):
        pgrm_ptr = 0
        bracket_map = self.brackets()
        while pgrm_ptr < len(self.pgrm):
            opcode = self.pgrm[pgrm_ptr]
            match opcode:
                case ">":
                    self.cell_ptr += 1
                case "<":
                    self.cell_ptr -= 1
                case "+":
                    self.tape[self.cell_ptr] = (self.tape[self.cell_ptr] + 1) % (256)
                case "-":
                    self.tape[self.cell_ptr] = (self.tape[self.cell_ptr] - 1) % (256)
                case ".":
                    print(chr(self.tape[self.cell_ptr]), end="")
                case ",":
                    self.tape[self.cell_ptr] = ord(input()[0])
                case "[":
                    if not self.tape[self.cell_ptr]:
                        pgrm_ptr = bracket_map[pgrm_ptr]
                case "]":
                    if self.tape[self.cell_ptr]:
                        pgrm_ptr = bracket_map[pgrm_ptr]
                case _:
                    raise Exception(f"Unknown opcode: {opcode}")
            pgrm_ptr += 1

    def cleanup(self, pgrm: str) -> list[str]:
        return list(
            filter(lambda x: x in [">", "<", "+", "-", ".", ",", "[", "]"], pgrm)
        )


if __name__ == "__main__":
    st = time.time()
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            pgrm = f.read()
        c = bf(pgrm).run()
        print(f"Time: {time.time() - st}")
    else:
        print(f"Usage: {sys.argv[0]} [brainfuck program]")
