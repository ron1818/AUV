import time
import serial
import pynmea2


def read(filename):
    f = open(filename)
    reader = pynmea2.NMEAStreamReader(f)

    while 1:
        for msg in reader.next():
          print(msg)


def read_serial(com):
    reader = pynmea2.NMEAStreamReader()

    while 1:
        data = com.read(16)
        print data
        try: 
            for msg in reader.next(data):
                print("parsing")
                print(msg.fields)
        except:
            print("cannot parse")
            continue

if __name__ == "__main__":
    ser = serial.Serial(
            port="/dev/ttyAMA0",
            baudrate=4800,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1)

    read_serial(ser)
