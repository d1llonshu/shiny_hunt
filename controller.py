import serial
from serial import Serial
from typing import Optional
import threading

_latest_cmd = None
_lock = threading.Lock()


BAUD = 115200

def init_serial(port: str, baud: int = BAUD) -> Serial:
    ser = serial.Serial(port, baud, timeout=1)
    print(f"Connected to {port} @ {baud} baud")
    return ser

def close_serial(ser: Serial):
    if ser is None:
        return
    try:
        print("Closing serial...")
        ser.close()
    except serial.SerialException as e:
        print(f"Could not close serial port: {e}")

def controller_sequence(ser: Serial, msg: str) -> bool:
    if ser is None:
        # print("Serial object is None; cannot write.")
        return False
    try:
        data = msg.strip().encode("utf-8")
        ser.write(data)
        return True
    except serial.SerialException as e:
        # print(f"Serial write failed: {e}")
        return False

def read_line(ser: Serial) -> Optional[str]:
    if ser is None:
        return None
    try:
        line = ser.readline()
        return line.decode("utf-8", errors="replace").rstrip("\r\n")
    except serial.SerialException as e:
        print(f"Serial read failed: {e}")
        return None

def test_commands(ser: Serial):
    while True:
        cmd = input("Enter a step: ")
        ser.write(cmd.strip().encode('utf-8'))
        if cmd == "1":
            output = read_line(ser)
            while output != "End Scripted Input":
                if output != None and len(output) > 0:
                    print(output)
                output = read_line(ser)
            if output:
                print(output)

def start_serial_reader(ser):
    threading.Thread(target=_reader_loop, args=(ser,), daemon=True).start()

def _reader_loop(ser):
    global _latest_cmd
    while True:
        try:
            line = read_line(ser)  # blocking call
            if line:  # ignore empty
                with _lock:
                    _latest_cmd = line.strip()
        except Exception as e:
            print("Serial reader error:", e)
            # optional: backoff or sleep briefly
            continue

def get_latest_command():
    with _lock:
        return _latest_cmd
    
def async_controller_sequence(ser, cmd):
    threading.Thread(target=lambda: controller_sequence(ser, cmd), daemon=True).start()

# while True:
#     cmd = input("Enter a command (A/B/X/Y U/D/L/R): ")
#     ser.write(cmd.strip().encode('utf-8'))

# try:
#     while True:
#         # line = ser.readline()
#         # if line:
#         #     print(line)
#         #     print(line.decode('utf-8', errors='replace').rstrip())
#         # else:
#             cmd = input("Enter a command (A/B/X/Y U/D/L/R): ")
#             ser.write(cmd.strip().encode('utf-8'))
# except KeyboardInterrupt:
#     ser.close()
#     print('\nSerial port closed.')

if __name__ == "__main__":
    ser = init_serial("COM8")
    test_commands(ser)
