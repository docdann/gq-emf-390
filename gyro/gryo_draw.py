import time
import serial
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


GETGYRO_COMMAND = 'GETGYRO'
GYRO_MAX_VALUE = 65536  # Maximum 16-bit value for gyroscope data

def send_gyro_command(serial_port, command):
    cmd_str = f"<{command}>>"
    serial_port.write(cmd_str.encode())

    response = serial_port.read(7)
    return response

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

def draw_lines(x_data, y_data, z_data):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glBegin(GL_LINES)

    scale = 0.0001  # Adjust this value to scale the lines accordingly
    
    for i in range(len(x_data) - 1):
        glColor3f(1, 0, 0)
        glVertex3f(x_data[i] * scale, y_data[i] * scale, z_data[i] * scale)
        glVertex3f(x_data[i + 1] * scale, y_data[i + 1] * scale, z_data[i + 1] * scale)

    glEnd()
    pygame.display.flip()

def main():
    com_port = 'COM4'
    baud_rate = 115200
    data_bits = 8
    stop_bits = serial.STOPBITS_ONE
    parity = serial.PARITY_NONE
    timeout = 5
    inter_byte_timeout = 0.1

    ser = None

    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -1)  # Adjust the z-value to change the camera distance

    x_data, y_data, z_data = [], [], []

    try:
        ser = serial.Serial(com_port, baud_rate, bytesize=data_bits, stopbits=stop_bits, parity=parity, timeout=timeout, inter_byte_timeout=inter_byte_timeout)
        time.sleep(1)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            response = send_gyro_command(ser, GETGYRO_COMMAND)
            print(f"Gyroscope data: {response.hex()}")

            x, y, z = parse_gyro_data(response, x_data[-1] if x_data else 0, y_data[-1] if y_data else 0, z_data[-1] if z_data else 0)

            x_data.append(x)
            y_data.append(y)
            z_data.append(z)

            draw_lines(x_data, y_data, z_data)
            pygame.time.wait(10)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if ser:
            ser.close()
            print("Connection closed")

if __name__ == '__main__':
    main()

