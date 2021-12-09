#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import signal
from sys import exit as sys_exit
from sys import stderr
from time import sleep

import serial
from crc import crc16
# pylint: disable=no-name-in-module
from yahdlc import (FRAME_ACK, FRAME_DATA, FRAME_NACK, FCSError, MessageError,
                    frame_data, get_data)
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

# Open the binary file for reading
file_handler = open("CSAM-5.2.1706.739.bin", "rb")

# Read the first three bytes from the binary file
data_byte = file_handler.read(7)

# Serial port configuration
ser = serial.Serial()
ser.port = "/dev/ttys013"
ser.baudrate = 9600
ser.timeout = 0

print("[*] Connection...")

try:
    ser.open()
except serial.SerialException as err:
    stderr.write(f"[x] Serial connection problem: {err}\n")
    sys_exit(1)

# Iterate the loop to read the remaining part of the file
for i in range(len(data_byte)):
    print("[*] Sending data frame...", )
    data_byte = file_handler.read(7)
    data = str(crc16(data_byte, 0, len(data_byte)))
    ser.write(frame_data(data, FRAME_DATA, 1))
    
print("[*] Waiting for (N)ACK...")

def timeout_handler(signum, frame):
    """
    Timeout handler.
    """

    raise TimeoutError("Timeout")


signal.signal(signal.SIGALRM, timeout_handler)
# 1-second timeout
signal.alarm(1)

while True:
    try:
        # 200 µs
        sleep(200 / 1000000.0)
        data, ftype, seq_no = get_data(ser.read(ser.inWaiting()))
        signal.alarm(0)
        break
    except MessageError:
        pass
    except FCSError:
        stderr.write("[x] Bad FCS\n")
        print("[*] Done")
        ser.close()
        sys_exit(0)
    except TimeoutError as err:
        stderr.write("[x] " + str(err) + "\n")
        print("[*] Done")
        ser.close()
        sys_exit(0)
    except KeyboardInterrupt:
        print("[*] Bye!")
        ser.close()
        sys_exit(0)

if ftype not in (FRAME_ACK, FRAME_NACK):
    stderr.write(f"[x] Bad frame type: {ftype}\n")
elif ftype == FRAME_ACK:
    print("[*] ACK received")

    if seq_no != 1:
        stderr.write(f"[x] Bad sequence number: {seq_no}\n")
    else:
        print("[*] Sequence number OK")
else:
    print("[*] NACK received")

    if seq_no != 0:
        stderr.write(f"[x] Bad sequence number: {seq_no}\n")
    else:
        print("[*] Sequence number OK")

print("[*] Done")
ser.close()
