import os

from LSCP import LSCPService


valid_id_combos = [(0x067B, 0x2303),  # USB serial
                   (0x0403, 0x6001)]  # FTDI cable
# device_snum = os.getenv('LSCPCABLESERIAL', None)  # If we are on the test station, use specified serial
dut = LSCPService(valid_id_combos, device_snum=None, baudrate=921600, rtscts=False, timeout=10, send_heartbeats=False)
