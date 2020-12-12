"""CPU functionality."""

import sys

# op-codes
LDI = 0b10000010  # 130
PRN = 0b01000111  # 71
HLT = 0b00000001  # 1
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
# op-codes for sprint
CMP = 0b10100111
JEQ = 0b01010101
JNE = 0b01010110
JMP = 0b01010100


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.PC = 0
        self.FL = 0b00000000  # 00000LGE
        self.ram = [0] * 256
        self.halted = False

    def load(self, filename):
        """Load a program into memory."""

        try:
            with open(filename) as f:
                address = 0
                for line in f:
                    line_split = line.split("#")
                    try:
                        binary_num = int(line_split[0], 2)
                        # print(binary_num)
                        self.ram_write(binary_num, address)
                        address += 1
                    except:
                        # can silently fail instead of making a print statement
                        # print("failed to make binary")
                        continue
        except FileNotFoundError:
            print("File not found ...")

        """
        address = 0

        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            0b10000010,  # LDI R0,8
            0b00000000,
            0b00001000,  # integer 8 to be stored
            0b01000111,  # PRN R0
            0b00000000,
            0b00000001,  # HLT
        ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1
        """

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] < self.reg[reg_b]:
                # print(f"{self.reg[cmd_a]} < {self.reg[cmd_b]}")
                self.FL = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                # print(f"{self.reg[cmd_a]} > {self.reg[cmd_b]}")
                self.FL = 0b00000010
            elif self.reg[reg_a] == self.reg[reg_b]:
                # print(f"{self.reg[cmd_a]} = {self.reg[cmd_b]}")
                self.FL = 0b00000001
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(
            f"TRACE: %02X | %02X %02X %02X |"
            % (
                self.PC,
                # self.fl,
                # self.ie,
                self.ram_read(self.PC),
                self.ram_read(self.PC + 1),
                self.ram_read(self.PC + 2),
            ),
            end="",
        )

        for i in range(8):
            print(" %02X" % self.reg[i], end="")

        print()

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def run(self):
        """Run the CPU."""
        while not self.halted:
            op = self.ram_read(self.PC)
            counter_advance = op >> 6
            cmd_a = self.ram_read(self.PC + 1)
            cmd_b = self.ram_read(self.PC + 2)

            if op == LDI:
                self.reg[cmd_a] = cmd_b
                # print("LDI success")
            elif op == PRN:
                print(self.reg[cmd_a])
            elif op == ADD:
                self.alu("ADD", cmd_a, cmd_b)
            elif op == MUL:
                self.alu("MUL", cmd_a, cmd_b)
                # self.reg[cmd_a] *= self.reg[cmd_b]
            elif op == PUSH:
                self.reg[7] -= 1
                self.ram_write(self.reg[cmd_a], self.reg[7])
            elif op == POP:
                self.reg[cmd_a] = self.ram_read(self.reg[7])
                self.reg[7] += 1
            elif op == HLT:
                print("Program Halted")
                # print(f"ram: {self.ram}")
                # print(f"regs: {self.reg}")
                self.halted = True
                # sys.exit(0)
            elif op == CALL:
                # stores the address of next instruction on top of the stack
                self.reg[7] -= 1
                self.ram_write(self.PC + 2, self.reg[7])
                # it jumps to the address stored in that register
                self.PC = self.reg[cmd_a]
                counter_advance -= 2  # adjust becuase we are jumping to the address
            elif op == RET:
                # doesn't take in any operands, sets the program counter to the topmost element of the stack and pop it
                self.PC = self.ram_read(self.reg[7])
                self.reg[7] += 1
                counter_advance -= 1  # adjust becuase we are jumping to the address
            # ! commands for sprint
            elif op == CMP:
                self.alu("CMP", cmd_a, cmd_b)
            elif op == JMP:
                # jump to address stored in given register
                self.PC = self.reg[cmd_a]
                counter_advance -= 2  # adjust becuase we are jumping to the address
            elif op == JEQ:
                # If E flag is set (1), jump to the address stored in the given register.
                mask = 0b00000001
                if self.FL & mask == 0b00000001:
                    self.PC = self.reg[cmd_a]
                    counter_advance -= 2  # adjust becuase we are jumping to the address
            elif op == JNE:
                # If E flag is clear (0), jump to the address stored in the given register.
                # print(self.FL)
                mask = 0b00000001
                if self.FL & mask == 0b00000000:
                    self.PC = self.reg[cmd_a]
                    counter_advance -= 2  # adjust becuase we are jumping to the address
            else:
                print("Error: not a valid instruction")
                break
            self.PC += counter_advance + 1
