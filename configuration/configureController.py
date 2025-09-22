import serial.tools.list_ports
from configuration.configHelper import print_linebreak

#Probably looking for USB-Enhanced-SERIAL CH343

#COMPUTER USB CORD RIGHT SIDE, SWITCH USB LEFT SIDE

def setup(uart_port : str = ""):
    print("Setting Up Controller Serial Communication...")
    og_uart = uart_port

    ports = list(serial.tools.list_ports.comports())
    uart_selected = False

    for p in ports:
        if uart_port == p.device:
            uart_selected = True
    if uart_port != "" and uart_selected == False:
        print("The provided COM port was not detected. You will be asked to select a new one.")
        print("Please see the below list of ports and make sure the device is plugged in.")

    if not uart_selected:
        print("List of Available Serial Ports:")
        print_linebreak()
        for p in ports:
            print(f"{p.device}: {p.description}")
    
    
    while not uart_selected:
        uart_port = input("Please select the COM port. ")
        for p in ports:
            if uart_port.lower() == p.device.lower():
                uart_selected = True


    updated = True 
    if og_uart == uart_port:
        updated = False

    return {"COM": uart_port.upper(), "updated":updated}