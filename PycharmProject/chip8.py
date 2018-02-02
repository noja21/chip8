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
    drawFlag = None

    # Chip8
    gfx = [None] * (64 * 32)  # Total amount of pixels: 2048
    key = [None] * 16

    pc = None  # Program counter
    opcode = None  # Current opcode
    I = None  # Index register
    sp = None  # Stack pointer

    V = [None] * 16  # V-regs (V0-VF)
    stack = [None] * 16  # Stack (16 levels)
    memory = [None] * 4096  # Memory (size = 4k)

    delay_timer = None  # Delay timer
    sound_timer = None  # Sound timer

    def __init__(self):
        pass

    def init(self):
        pc = 0x200  # Program counter starts at 0x200 (Start adress program)
        opcode = 0  # Reset current opcode
        I = 0  # Reset index register
        sp = 0  # Reset stack pointer

        # Clear display
        for i in range(2048):
            gfx[i] = 0

        # Clear stack
        for i in range(16):
            stack[i] = 0

        for i in range(16):
            key[i] = V[i] = 0

        # Clear memory
        for i in range(4096):
            memory[i] = 0

        # Load fontset
        for i in range(80):
            memory[i] = chip8_fontset[i]

        # Reset timers
        delay_timer = 0
        sound_timer = 0

        # Clear screen once
        drawFlag = True

        random.seed(datetime.now())
