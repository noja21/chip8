import sys
import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from chip8 import *

# Display size
SCREEN_WIDTH = 64
SCREEN_HEIGHT = 32

myChip8 = Chip8()
modifier = 5

# Window size
display_width = SCREEN_WIDTH * modifier
display_height = SCREEN_HEIGHT * modifier

# Use new drawing method
DRAWWITHTEXTURE = True
screenData = np.zeros(shape=(SCREEN_HEIGHT, SCREEN_WIDTH, 3), dtype=np.uint8)


def main(argc, argv):
    if argc < 2:
        print("Usage: phip8 chip8application\n")
        return 1

    # Load game
    if not myChip8.loadApplication(argv[1]):
        return 1

    # Setup OpenGL
    glutInit(argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)

    glutInitWindowSize(display_width, display_height)
    glutInitWindowPosition(0, 0)
    glutCreateWindow("Phip8 by Jinhan Kim")

    glutDisplayFunc(display)
    glutIdleFunc(display)
    glutReshapeFunc(reshape_window)
    glutKeyboardFunc(keyboardDown)
    glutKeyboardUpFunc(keyboardUp)

    if DRAWWITHTEXTURE:
        setupTexture()

    glutMainLoop()

    return 0


# Setup Texture
def setupTexture():
    global screenData

    # Clear screen
    for y in range(SCREEN_HEIGHT):
        for x in range(SCREEN_WIDTH):
            screenData[y][x][0] = screenData[y][x][1] = screenData[y][x][2] = 0

    # Create a texture
    glTexImage2D(GL_TEXTURE_2D, 0, 3, SCREEN_WIDTH, SCREEN_HEIGHT, 0, GL_RGB, GL_UNSIGNED_BYTE, screenData)

    # Set up the texture
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)

    # Enable textures
    glEnable(GL_TEXTURE_2D)


def updateTexture(c8):
    global screenData

    # Update pixels
    for y in range(32):
        for x in range(64):
            if c8.gfx[(y * 64) + x] == 0:
                # screenData[y][x][0] = screenData[y][x][1] = screenData[y][x][2] = 0  # Disabled
                screenData[y][x][0] = 64; screenData[y][x][1] = 64; screenData[y][x][2] = 64  # Disabled
            else:
                # screenData[y][x][0] = screenData[y][x][1] = screenData[y][x][2] = 255  # Enabled
                screenData[y][x][0] = 255; screenData[y][x][1] = 0; screenData[y][x][2] = 255  # Enabled

    # Update Texture
    glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, GL_RGB, GL_UNSIGNED_BYTE, screenData)

    glBegin(GL_QUADS)

    glTexCoord2d(0.0, 0.0)
    glVertex2d(0.0, 0.0)

    glTexCoord2d(1.0, 0.0)
    glVertex2d(display_width, 0.0)

    glTexCoord2d(1.0, 1.0)
    glVertex2d(display_width, display_height)

    glTexCoord2d(0.0, 1.0)
    glVertex2d(0.0, display_height)

    glEnd()


# Old gfx code
def drawPixel(x, y):
    glBegin(GL_QUADS)
    glVertex3f((x * modifier) + 0.0, (y * modifier) + 0.0, 0.0)
    glVertex3f((x * modifier) + 0.0, (y * modifier) + modifier, 0.0)
    glVertex3f((x * modifier) + modifier, (y * modifier) + modifier, 0.0)
    glVertex3f((x * modifier) + modifier, (y * modifier) + 0.0, 0.0)
    glEnd()


def updateQuads(c8):
    # Draw
    for y in range(32):
        for x in range(64):
            if c8.gfx[(y * 64) + x] == 0:
                glColor3f(0.0, 0.0, 0.0)
            else:
                glColor3f(1.0, 1.0, 1.0)

            drawPixel(x, y)


def display():
    myChip8.emulateCycle()

    if myChip8.drawFlag:
        # Clear framebuffer
        glClear(GL_COLOR_BUFFER_BIT)

        if DRAWWITHTEXTURE:
            updateTexture(myChip8)
        else:
            updateQuads(myChip8)

        # Swap buffers!
        glutSwapBuffers()

        # Processed frame
        myChip8.drawFlag = False


def reshape_window(w, h):
    glClearColor(0.0, 0.0, 0.5, 0.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, w, h, 0)
    glMatrixMode(GL_MODELVIEW)
    glViewport(0, 0, w, h)

    # Resize quad
    global display_width
    global display_height
    display_width = w
    display_height = h


def keyboardDown(key, x, y):
    if key == b'\x1b':  # esc
        sys.exit(0)

    if key == b'1':
        myChip8.key[0x1] = 1
    elif key == b'2':
        myChip8.key[0x2] = 1
    elif key == b'3':
        myChip8.key[0x3] = 1
    elif key == b'4':
        myChip8.key[0xC] = 1

    elif key == b'q':
        myChip8.key[0x4] = 1
    elif key == b'w':
        myChip8.key[0x5] = 1
    elif key == b'e':
        myChip8.key[0x6] = 1
    elif key == b'r':
        myChip8.key[0xD] = 1

    elif key == b'a':
        myChip8.key[0x7] = 1
    elif key == b's':
        myChip8.key[0x8] = 1
    elif key == b'd':
        myChip8.key[0x9] = 1
    elif key == b'f':
        myChip8.key[0xE] = 1

    elif key == b'z':
        myChip8.key[0xA] = 1
    elif key == b'x':
        myChip8.key[0x0] = 1
    elif key == b'c':
        myChip8.key[0xB] = 1
    elif key == b'v':
        myChip8.key[0xF] = 1

    print("Press key %s" % key)


def keyboardUp(key, x, y):
    if key == b'1':
        myChip8.key[0x1] = 0
    elif key == b'2':
        myChip8.key[0x2] = 0
    elif key == b'3':
        myChip8.key[0x3] = 0
    elif key == b'4':
        myChip8.key[0xC] = 0

    elif key == b'q':
        myChip8.key[0x4] = 0
    elif key == b'w':
        myChip8.key[0x5] = 0
    elif key == b'e':
        myChip8.key[0x6] = 0
    elif key == b'r':
        myChip8.key[0xD] = 0

    elif key == b'a':
        myChip8.key[0x7] = 0
    elif key == b's':
        myChip8.key[0x8] = 0
    elif key == b'd':
        myChip8.key[0x9] = 0
    elif key == b'f':
        myChip8.key[0xE] = 0

    elif key == b'z':
        myChip8.key[0xA] = 0
    elif key == b'x':
        myChip8.key[0x0] = 0
    elif key == b'c':
        myChip8.key[0xB] = 0
    elif key == b'v':
        myChip8.key[0xF] = 0


main(2, ["phip8", "/Users/jinhankim/github/chip8/chip8_applications/BLINKY"])
