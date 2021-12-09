#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sys import exit as sys_exit
from sys import stderr
from time import sleep

import serial

# pylint: disable=no-name-in-module
from yahdlc import (FRAME_ACK, FRAME_DATA, FRAME_NACK, FCSError, MessageError,
                    frame_data, get_data)
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

# Serial port configuration
ser = serial.Serial()
ser.port = "/dev/ttys014"
ser.baudrate = 9600
ser.timeout = 0

print("[*] Connection...")

try:
    ser.open()
except serial.SerialException as err:
    stderr.write(f"[x] Serial connection problem: {err}\n")
    sys_exit(1)

print("[*] Waiting for data...")

while True:
    try:
        # 200 µs
        sleep(200 / 1000000.0)
        data, ftype, seq_no = get_data(ser.read(ser.inWaiting()))
        break
    except MessageError:
        pass
    except FCSError:
        stderr.write("[x] Bad FCS\n")
        print("[*] Sending NACK...")
        ser.write(frame_data("", FRAME_NACK, 0))
        ser.close()
        sys_exit(0)
    except KeyboardInterrupt:
        ser.close()
        print("[*] Bye!")
        sys_exit(0)

FRAME_ERROR = False

if ftype != FRAME_DATA:
    stderr.write(f"[x] Bad frame type: {ftype}\n")
    FRAME_ERROR = True
else:
    # file = open("sample.bin", "wb")
    # file.write(b"This binary string will be written to sample.bin")
    # file.close()
    print(f"[*] Received data: {data}")
    print("[*] Data frame received")

if seq_no != 0:
    stderr.write(f"[x] Bad sequence number: {seq_no}\n")
    FRAME_ERROR = True
else:
    print("[*] Sequence number OK")

if FRAME_ERROR is False:
    print("[*] Sending ACK ...")
    ser.write(frame_data("", FRAME_ACK, 1))
else:
    print("[*] Sending NACK ...")
    ser.write(frame_data("", FRAME_NACK, 0))

print("[*] Done")
ser.close()
