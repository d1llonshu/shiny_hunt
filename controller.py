import serial
import sys
import serial.tools.list_ports

PORT = "COM8"   
BAUD = 115200 #sync to comp?

ports = list(serial.tools.list_ports.comports())
for p in ports:
    print(f"{p.device}: {p.description}")

try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
except serial.SerialException as e:
    print("Could not open serial port:", e)
    sys.exit(1)

print(f"Connected to {PORT} @ {BAUD} baud")

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
