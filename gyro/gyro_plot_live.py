import time
import serial
import matplotlib.pyplot as plt
import numpy as np

GETGYRO_COMMAND = 'GETGYRO'
GYRO_MAX_VALUE = 65536  # Maximum 16-bit value for gyroscope data

def send_gyro_command(serial_port, command):
    cmd_str = f"<{command}>>"
    serial_port.write(cmd_str.encode())

    response = serial_port.read(7)
    return response

def plot_gyro_data(time_data, x_data, y_data, z_data):
    plt.clf()

    plt.plot(time_data, x_data, label='X')
    plt.plot(time_data, y_data, label='Y')
    plt.plot(time_data, z_data, label='Z')

    plt.xlabel('Time')
    plt.ylabel('Position Data')
    plt.title('Gyroscope Data')
    plt.legend()
    plt.pause(0.01)

def parse_gyro_data(response, prev_x, prev_y, prev_z):
    x = (response[0] << 8) + response[1]
    y = (response[2] << 8) + response[3]
    z = (response[4] << 8) + response[5]

    # Handle the case when the position data transitions from the minimum value to the maximum value or vice versa
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

    plt.ion()

    x_data, y_data, z_data, time_data = [], [], [], []

    try:
        ser = serial.Serial(com_port, baud_rate, bytesize=data_bits, stopbits=stop_bits, parity=parity, timeout=timeout, inter_byte_timeout=inter_byte_timeout)
        time.sleep(1)

        start_time = time.time()

        while True:
            response = send_gyro_command(ser, GETGYRO_COMMAND)
            print(f"Gyroscope data: {response.hex()}")

            x, y, z = parse_gyro_data(response, x_data[-1] if x_data else 0, y_data[-1] if y_data else 0, z_data[-1] if z_data else 0)

            elapsed_time = time.time() - start_time

            x_data.append(x)
            y_data.append(y)
            z_data.append(z)
            time_data.append(elapsed_time)

            plot_gyro_data(time_data, x_data, y_data, z_data)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if ser:
            ser.close()
            print("Connection closed")

if __name__ == '__main__':
    main()
