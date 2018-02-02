import random
from datetime import datetime

chip8_fontset = [
    0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
    0x20, 0x60, 0x20, 0x20, 0x70,  # 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
    0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
    0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
    0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
    0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
    0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
    0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
    0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
    0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
    0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
    0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
    0xF0, 0x80, 0xF0, 0x80, 0x80  # F
]


class Chip8:
    def __init__(self):
        self.drawFlag = None

        # Chip8
        self.gfx = [None] * (64 * 32)  # Total amount of pixels: 2048
        self.key = [None] * 16

        self.pc = None  # Program counter
        self.opcode = None  # Current opcode
        self.I = None  # Index register
        self.sp = None  # Stack pointer

        self.V = [None] * 16  # V-regs (V0-VF)
        self.stack = [None] * 16  # Stack (16 levels)
        self.memory = [None] * 4096  # Memory (size = 4k)

        self.delay_timer = None  # Delay timer
        self.sound_timer = None  # Sound timer

    def __del__(self):
        pass

    def init(self):
        self.pc = 0x200  # Program counter starts at 0x200 (Start adress program)
        self.opcode = 0  # Reset current opcode
        self.I = 0  # Reset index register
        self.sp = 0  # Reset stack pointer

        # Clear display
        for i in range(2048):
            self.gfx[i] = 0

        # Clear stack
        for i in range(16):
            self.stack[i] = 0

        for i in range(16):
            self.key[i] = self.V[i] = 0

        # Clear memory
        for i in range(4096):
            self.memory[i] = 0

        # Load fontset
        for i in range(80):
            self.memory[i] = chip8_fontset[i]

        # Reset timers
        self.delay_timer = 0
        self.sound_timer = 0

        # Clear screen once
        self.drawFlag = True

        random.seed(datetime.now())
