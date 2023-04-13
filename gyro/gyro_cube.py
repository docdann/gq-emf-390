import time
import serial
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

GETGYRO_COMMAND = 'GETGYRO'
GYRO_MAX_VALUE = 65536  # Maximum 16-bit value for gyroscope data

def send_gyro_command(serial_port, command):
    cmd_str = f"<{command}>>"
    serial_port.write(cmd_str.encode())

    response = serial_port.read(7)
    return response

def draw_cube(x_angle, y_angle, z_angle):
    vertices = [
        [1, -1, -1],
        [1, 1, -1],
        [-1, 1, -1],
        [-1, -1, -1],
        [1, -1, 1],
        [1, 1, 1],
        [-1, -1, 1],
        [-1, 1, 1]
    ]

    edges = (
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 0),
        (4, 5),
        (5, 7),
        (7, 6),
        (6, 4),
        (0, 4),
        (1, 5),
        (2, 7),
        (3, 6)
    )

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(0, 0, -5, 0, 0, 0, 0, 1, 0)
    glTranslatef(0.0, 0.0, -7.0)
    glRotatef(x_angle, 1, 0, 0)
    glRotatef(y_angle, 0, 1, 0)
    glRotatef(z_angle, 0, 0, 1)

    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

    pygame.display.flip()

def parse_gyro_data(response, prev_x, prev_y, prev_z):
    x = (response[0] << 8) + response[1]
    y = (response[2] << 8) + response[3]
    z = (response[4] << 8) + response[5]

    if x < prev_x - GYRO_MAX_VALUE/2:
        x += GYRO_MAX_VALUE
    elif x > prev_x + GYRO_MAX_VALUE/2:
        x -= GYRO_MAX_VALUE

    if y < prev_y - GYRO_MAX_VALUE/2:
        y += GYRO_MAX_VALUE
    elif y > prev_y + GYRO_MAX_VALUE/2:
        y -= GYRO_MAX_VALUE

    if z < prev_z - GYRO_MAX_VALUE/2:
        z += GYRO_MAX_VALUE
    elif z > prev_z + GYRO_MAX_VALUE/2:
        z -= GYRO_MAX_VALUE

    return x, y, z

def main():
    com_port = 'COM4'
    baud_rate = 115200
    data_bits = 8
    stop_bits = serial.STOPBITS_ONE
    parity = serial.PARITY_NONE
    timeout = 5
    inter_byte_timeout = 0.1

    ser = None

    try:
        ser = serial.Serial(com_port, baud_rate, bytesize=data_bits, stopbits=stop_bits, parity=parity,
                            timeout=timeout, inter_byte_timeout=inter_byte_timeout)
        time.sleep(1)

        # Initialize Pygame
        pygame.init()
        display = (800, 600)
        pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
        gluPerspective(45, (display[0] / display[1]), 0.1, 100.0)

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    quit()

            response = send_gyro_command(ser, GETGYRO_COMMAND)
            print(f"Gyroscope data: {response.hex()}")

            x, y, z = parse_gyro_data(response, 0, 0, 0)

            x_angle = x * 360 / GYRO_MAX_VALUE
            y_angle = y * 360 / GYRO_MAX_VALUE
            z_angle = z * 360 / GYRO_MAX_VALUE

            # Swap X and Z axes and invert Z axis
            draw_cube(z_angle, y_angle, -x_angle)
            pygame.time.wait(10)  # Limit the frame rate

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if ser:
            ser.close()
            print("Connection closed")

if __name__ == '__main__':
    main()




