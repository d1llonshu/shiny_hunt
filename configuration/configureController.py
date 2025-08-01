import serial.tools.list_ports
from configuration.configHelper import print_linebreak

#Probably looking for USB-Enhanced-SERIAL CH343

def setup(uart_port : str = "", usb_port : str = ""):
    print("Setting Up Controller Serial Communication...")
    og_uart = uart_port
    og_usb = usb_port

    ports = list(serial.tools.list_ports.comports())
    usb_selected = False
    uart_selected = False

    for p in ports:
        if uart_port == p.device:
            uart_selected = True

    # USB/Upload port doesn't have to be plugged in so i presume we just have to take their word for it
    # Technically we don't even need it
    if usb_port:
        usb_selected = True

    if usb_port != "" and usb_port.lower() == uart_port.lower():
        print("Upload and COM ports cannot be the same. You will be asked to re-select both.")
        usb_selected = False
        uart_selected = False

    if not usb_selected or not uart_selected:
        print("List of Available Serial Ports:")
        print_linebreak()
        for p in ports:
            print(f"{p.device}: {p.description}")
    
    while not usb_selected:
        usb_port = input("Please select the upload port. If the port you are looking for is not there, please abort and try again.")
        for p in ports:
            if usb_port.lower() == p.device.lower():
                usb_selected = True
    
    while not uart_selected:
        uart_port = input("Please select the COM port. It cannot be the same as the upload port. If the port you are looking for is not there, please abort and try again.")
        for p in ports:
            if uart_port.lower() == p.device.lower() and uart_port.lower() != usb_port.lower():
                uart_selected = True
            elif uart_port.lower() == p.device.lower() and uart_port.lower() != usb_port.lower():
                print("The COM port cannot be the same as the upload port.")

    updated = True 
    if og_uart == uart_port and og_usb == usb_port:
        updated = False

    return {"Upload":usb_port.upper(), "COM": uart_port.upper(), "updated":updated}