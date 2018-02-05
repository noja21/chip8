import os
import sys
import random
import numpy as np
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
        self.drawFlag = False

        # Chip8
        self.gfx = [0] * (64 * 32)  # Total amount of pixels: 2048
        self.key = [0] * 16

        self.pc = 0  # Program counter
        self.opcode = 0  # Current opcode
        self.I = 0  # Index register
        self.sp = 0  # Stack pointer

        self.V = [0] * 16  # V registers (V0-VF)
        self.stack = [0] * 16  # Stack (16 levels)
        self.memory = [0] * 4096  # Memory (size = 4k)

        self.delay_timer = 0  # Delay timer
        self.sound_timer = 0  # Sound timer

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

    def emulateCycle(self):
        print("HERE: emulateCycle()")

        # Fetch opcode
        self.opcode = self.memory[self.pc] << 8 | self.memory[self.pc + 1]
        print("HERE opcode: %d" % self.opcode)

        # Process opcode
        first_nibble = self.opcode & 0xF000
        last_nibble = self.opcode & 0x000F

        address_NNN = self.opcode & 0x0FFF
        NN = self.opcode & 0x00FF

        VX_idx = (self.opcode & 0x0F00) >> 8
        VX = np.uint8(self.V[VX_idx])  # assign case and value case co-exist
        #print("HERE VX: %d" % VX)
        VY = np.uint8(self.V[(self.opcode & 0x00F0) >> 4])  # only value case exist
        #print("HERE VY: %d" % VY)
        #print("HERE (self.opcode & 0x00F0) >> 4: %d" % ((self.opcode & 0x00F0) >> 4))

        # VF = self.V[0xF] # only assign case exist. python not support define macros

        if first_nibble == 0x0000:
            if last_nibble == 0x0000:  # 0x00E0: Clears the screen
                for i in range(2048):
                    self.gfx[i] = 0x0
                self.drawFlag = True
                self.pc = self.pc + 2

            elif last_nibble == 0x000E:  # 0x00EE: Returns from subroutine
                self.sp = self.sp - 1  # 16 levels of stack, decrease stack pointer to prevent overwrite
                self.pc = self.stack[
                    self.sp]  # Put the stored return address from the stack back into the program counter
                self.pc = self.pc + 2  # Don't forget to increase the program counter!

            else:
                print("Unknown opcode [0x0000]: 0x%X" % self.opcode)

        elif first_nibble == 0x1000:  # 0x1NNN: Jumps to address NNN
            self.pc = address_NNN

        elif first_nibble == 0x2000:  # 0x2NNN: Calls subroutine at NNN.
            self.stack[self.sp] = self.pc  # Store current address in stack
            self.sp = self.sp + 1  # Increment stack pointer
            self.pc = address_NNN  # Set the program counter to the address at NNN

        elif first_nibble == 0x3000:  # 0x3XNN: Skips the next instruction if VX equals NN
            if VX == NN:
                self.pc = self.pc + 4
            else:
                self.pc = self.pc + 2

        elif first_nibble == 0x4000:  # 0x4XNN: Skips the next instruction if VX doesn't equal NN
            if VX != NN:
                self.pc = self.pc + 4
            else:
                self.pc = self.pc + 2

        elif first_nibble == 0x5000:  # 0x5XY0: Skips the next instruction if VX equals VY.
            if VX == VY:
                self.pc = self.pc + 4
            else:
                self.pc = self.pc + 2

        elif first_nibble == 0x6000:  # 0x6XNN: Sets VX to NN.
            self.V[VX_idx] = NN
            self.pc = self.pc + 2

        elif first_nibble == 0x7000:  # 0x7XNN: Adds NN to VX.
            self.V[VX_idx] = VX + NN
            self.pc = self.pc + 2

        elif first_nibble == 0x8000:
            if last_nibble == 0x0000:  # 0x8XY0: Sets VX to the value of VY
                self.V[VX_idx] = VY
                self.pc = self.pc + 2

            elif last_nibble == 0x0001:  # 0x8XY1: Sets VX to "VX OR VY"
                self.V[VX_idx] = VX | VY
                self.pc = self.pc + 2

            elif last_nibble == 0x0002:  # 0x8XY2: Sets VX to "VX AND VY"
                self.V[VX_idx] = VX & VY
                self.pc = self.pc + 2

            elif last_nibble == 0x0003:  # 0x8XY3: Sets VX to "VX XOR VY"
                self.V[VX_idx] = VX ^ VY
                self.pc = self.pc + 2

            elif last_nibble == 0x0004:  # 0x8XY4: Adds VY to VX. VF is set to 1 when there's a carry, and to 0 when there isn't
                if VY > (0xFF - VX):
                    self.V[0xF] = 1  # carry
                else:
                    self.V[0xF] = 0
                self.V[VX_idx] = VX + VY
                self.pc = self.pc + 2

            elif last_nibble == 0x0005:  # 0x8XY5: VY is subtracted from VX. VF is set to 0 when there's a borrow, and 1 when there isn't
                if VY > VX:
                    self.V[0xF] = 0  # there is a borrow
                else:
                    self.V[0xF] = 1
                self.V[VX_idx] = VX - VY
                self.pc = self.pc + 2

            elif last_nibble == 0x0006:  # 0x8XY6: Shifts VX right by one. VF is set to the value of the least significant bit of VX before the shift
                self.V[0xF] = VX & 0x1
                self.V[VX_idx] = VX >> 1
                self.pc = self.pc + 2

            elif last_nibble == 0x0007:  # 0x8XY7: Sets VX to VY minus VX. VF is set to 0 when there's a borrow, and 1 when there isn't
                if VX > VY:  # VY-VX
                    self.V[0xF] = 0  # there is a borrow
                else:
                    self.V[0xF] = 1
                self.V[VX_idx] = VY - VX
                self.pc = self.pc + 2

            elif last_nibble == 0x000E:  # 0x8XYE: Shifts VX left by one. VF is set to the value of the most significant bit of VX before the shift
                self.V[0xF] = VX >> 7
                self.V[VX_idx] = VX << 1
                self.pc = self.pc + 2

            else:
                print("Unknown opcode [0x8000]: 0x%X" % self.opcode)

        elif first_nibble == 0x9000:  # 0x9XY0: Skips the next instruction if VX doesn't equal VY
            if VX != VY:
                self.pc = self.pc + 4
            else:
                self.pc = self.pc + 2

        elif first_nibble == 0xA000:  # ANNN: Sets I to the address NNN
            self.I = address_NNN
            self.pc = self.pc + 2

        elif first_nibble == 0xB000:  # BNNN: Jumps to the address NNN plus V0
            self.pc = address_NNN + self.V[0]

        elif first_nibble == 0xC000:  # CXNN: Sets VX to a random number and NN
            self.V[VX_idx] = (random.randint(0, 32767) % 0xFF) & NN
            self.pc = self.pc + 2

        elif first_nibble == 0xD000:  # DXYN: Draws a sprite at coordinate (VX, VY) that has a width of 8 pixels and a height of N pixels.
            # Each row of 8 pixels is read as bit-coded starting from memory location I;
            # I value doesn't change after the execution of this instruction.
            # VF is set to 1 if any screen pixels are flipped from set to unset when the sprite is drawn,
            # and to 0 if that doesn't happen
            x = VX  # x = self.V[(self.opcode & 0x0F00) >> 8]
            y = VY  # y = self.V[(self.opcode & 0x00F0) >> 4]
            print("HERE x, y: (%d, %d)" % (x, y))
            height = last_nibble  # height = self.opcode & 0x000F
            #print("HERE height: %d" % height)
            pixel = None

            self.V[0xF] = 0
            for yline in range(height):
                pixel = self.memory[self.I + yline]
                for xline in range(8):
                    #print("HERE (pixel & (0x80 >> xline)): %d" % (pixel & (0x80 >> xline)))
                    if (pixel & (0x80 >> xline)) != 0:
                        # idx max: 2047, idx error: 2174 for pong2.c8
                        # idx max: 2047, idx error: 18341 for tetris.c8. VX = 37, VY = 286
                        print("HERE: %d" % (x + xline + ((y + yline) * 64)))

                        if self.gfx[x + xline + ((y + yline) * 64)] == 1:
                            self.V[0xF] = 1
                        self.gfx[x + xline + ((y + yline) * 64)] = self.gfx[x + xline + ((y + yline) * 64)] ^ 1

            self.drawFlag = True
            self.pc = self.pc + 2

        elif first_nibble == 0xE000:
            if NN == 0x009E:  # EX9E: Skips the next instruction if the key stored in VX is pressed
                if self.key[VX] != 0:
                    self.pc = self.pc + 4
                else:
                    self.pc = self.pc + 2

            elif NN == 0x00A1:  # EXA1: Skips the next instruction if the key stored in VX isn't pressed
                if self.key[VX] == 0:
                    self.pc = self.pc + 4
                else:
                    self.pc = self.pc + 2

            else:
                print("Unknown opcode [0xE000]: 0x%X" % self.opcode)

        elif first_nibble == 0xF000:
            if NN == 0x0007:  # FX07: Sets VX to the value of the delay timer
                self.V[VX_idx] = self.delay_timer
                self.pc = self.pc + 2

            elif NN == 0x000A:  # FX0A: A key press is awaited, and then stored in VX
                keypress = False

                for i in range(16):
                    if self.key[i] != 0:
                        self.V[VX_idx] = i
                        keypress = True

                # If we didn't received a keypress, skip this cycle and try again.
                if not keypress:
                    return

                self.pc = self.pc + 2

            elif NN == 0x0015:  # FX15: Sets the delay timer to VX
                self.delay_timer = VX
                self.pc = self.pc + 2

            elif NN == 0x0018:  # FX18: Sets the sound timer to VX
                self.sound_timer = VX
                self.pc = self.pc + 2

            elif NN == 0x001E:  # FX1E: Adds VX to I
                if (self.I + VX) > 0xFFF:  # VF is set to 1 when range overflow (I+VX>0xFFF), and 0 when there isn't.
                    self.V[0xF] = 1
                else:
                    self.V[0xF] = 0
                self.I = self.I + VX
                self.pc = self.pc + 2

            elif NN == 0x0029:  # FX29: Sets I to the location of the sprite for the character in VX. Characters 0-F (in hexadecimal) are represented by a 4x5 font
                self.I = VX * 0x5
                self.pc = self.pc + 2

            elif NN == 0x0033:  # FX33: Stores the Binary-coded decimal representation of VX at the addresses I, I plus 1, and I plus 2
                self.memory[self.I] = VX // 100
                self.memory[self.I + 1] = (VX // 10) % 10
                self.memory[self.I + 2] = (VX % 100) % 10
                self.pc = self.pc + 2

            elif NN == 0x0055:  # FX55: Stores V0 to VX in memory starting at address I
                for i in range(VX_idx + 1):
                    self.memory[self.I + i] = self.V[i]

                # On the original interpreter, when the operation is done, I = I + X + 1.
                self.I = self.I + VX_idx + 1
                self.pc = self.pc + 2

            elif NN == 0x0065:  # FX65: Fills V0 to VX with values from memory starting at address I
                for i in range(VX_idx + 1):
                    self.V[i] = self.memory[self.I + i]

                # On the original interpreter, when the operation is done, I = I + X + 1.
                self.I = self.I + VX_idx + 1
                self.pc = self.pc + 2

            else:
                print("Unknown opcode [0xF000]: 0x%X" % self.opcode)

        else:
            print("Unknown opcode: 0x%X" % self.opcode)

        # Update timers
        if self.delay_timer > 0:
            self.delay_timer = self.delay_timer - 1

        if self.sound_timer > 0:
            if self.sound_timer == 1:
                print("BEEP!")
            self.sound_timer = self.sound_timer - 1

    def debugRender(self):
        # Draw
        for y in range(32):
            for x in range(64):
                if self.gfx[(y * 64) + x] == 0:
                    print("O", end='')
                else:
                    print(" ", end='')
            print("")
        print("")

    def loadApplication(self, filename):
        self.init()
        print("Loading: %s" % filename)

        # Open file
        try:
            pFile = open(filename, "rb")
        except:
            print("your message", file=sys.stderr)
            return False

        # Check file size
        lSize = os.path.getsize(filename)
        print("Filesize: %d" % lSize)

        # Copy the file into the buffer
        mybuffer = pFile.read()
        result = len(mybuffer)
        if result != lSize:
            print("Reading error", file=sys.stderr)
            return False

        # Copy buffer to Chip8 memory
        if (4096 - 512) > lSize:
            for i in range(lSize):
                self.memory[i + 512] = mybuffer[i]
        else:
            print("Error: ROM too big for memory")

        # Close file
        pFile.close()

        return True
