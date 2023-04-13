import time
import serial
from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
import numpy as np

GETMODE_COMMAND = 'GETMODE'
GETBANDDATA_COMMAND = 'GETBANDDATA'

def send_rf_command(serial_port, command):
    cmd_str = f"<{command}>>"
    serial_port.write(cmd_str.encode())

    response = serial_port.readline().decode().strip()
    return response

def plot_band_data(data, mode):
    # Clear the screen
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Set up the viewport and projection matrix
    glViewport(0, 0, 800, 600)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, 128, -120, 0)

    # Set up the modelview matrix
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Draw the data as a line strip
    glBegin(GL_LINE_STRIP)
    for i in range(len(data)):
        glVertex2f(i, data[i])
    glEnd()

    # Set the window title
    pygame.display.set_caption(f"Band Data ({mode})")

    # Swap the buffers to display the image
    pygame.display.flip()

def parse_band_data(response, data, mode):
    # Strip off the "dBm" suffix and split the response string into a list of values
    values = [int(x) for x in response.rstrip(' dBm').split(',') if x]

    # Update the plot with the new data
    for i, value in enumerate(values):
        if i < len(data):
            data[i] = value
        else:
            data.pop(0)
            data.append(value)
    plot_band_data(data, mode)

def main():
    global data, mode

    com_port = 'COM4'
    baud_rate = 115200
    data_bits = 8
    stop_bits = serial.STOPBITS_ONE
    parity = serial.PARITY_NONE
    timeout = 0.08

    data = [0] * 128  # Set the length of the data list to 128
    mode = ""

    try:
        ser = serial.Serial(com_port, baud_rate, bytesize=data_bits, stopbits=stop_bits, parity=parity, timeout=timeout)
        time.sleep(1)

        response = send_rf_command(ser, GETMODE_COMMAND)
        print(f"Mode: {response}")
        mode = response

        # Initialize the Pygame library
        pygame.init()

        # Set up the OpenGL context
        pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)
        glClearColor(0.0, 0.0, 0.0, 0.0)

        while True:
            response = send_rf_command(ser, GETBANDDATA_COMMAND)
            print(f"Band data: {response}")

            parse_band_data(response, data, mode)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if ser:
            ser.close()
            print("Connection closed")

if __name__ == '__main__':
    main()
