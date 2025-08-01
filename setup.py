from configuration import configureAudioDevice
from configuration import configureVideoDevice
from configuration import configureBoundingBox
from configuration import configureController
from configuration import configHelper

import json

CONFIG_PATH = "config.json"

def setup(hunt_name):
    needs_updating = False
    # Load existing (or start fresh if missing)
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
        f.close()
    except FileNotFoundError:
        config = {}
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)
        f.close()

    try:
        with open(CONFIG_PATH, "r") as f:
            data = config[hunt_name]
            print(f"Config found for {hunt_name}, checking validity of config")

    except:
            print(f"No config found for {hunt_name}, generating new config.")
            data = {}

    configHelper.print_linebreak()
    keys = data.keys()

    if "audio_device_index" not in keys or configureAudioDevice.testAudioDevice(data["audio_device_index"]) < 0:
        audio_device : configureAudioDevice.DeviceInfo = configureAudioDevice.setup()
        data["audio_device_index"] = audio_device["index"]
        needs_updating = True
    print("Audio Device Selected Sucessfully!")
    configHelper.print_linebreak()

    if "video_device_index" not in keys or not configureVideoDevice.saveSampleVideo(data["video_device_index"]):
        video_device : int = configureVideoDevice.setup()
        data["video_device_index"] = video_device
        needs_updating = True
    print("Video Device Selected Sucessfully!")
    configHelper.print_linebreak()

    if "shiny_bounding_box" not in keys or not configureBoundingBox.validateBoundingBox(data["shiny_bounding_box"]):
        bounding_box = configureBoundingBox.setup(data["video_device_index"])
        data["shiny_bounding_box"] = bounding_box
        needs_updating = True

    print("Bounding Box Set Sucessfully!")
    configHelper.print_linebreak()

    if "controller_com_port" not in keys:
        if "controller_upload_port" not in keys:
            controller_ports = configureController.setup()
        else:
            controller_ports = configureController.setup(usb_port=data["controller_upload_port"])
        data["controller_com_port"] = controller_ports["COM"]
        data["controller_upload_port"] = controller_ports["Upload"]
        configHelper.print_linebreak()

    else:
        controller_ports = configureController.setup(uart_port=data["controller_com_port"], usb_port=data["controller_upload_port"])

    print("Controller Serial Ports Selected Sucessfully!")
    configHelper.print_linebreak()

    # Rewrite config if needed
    if needs_updating or controller_ports["updated"]:
        print("Updating Config...")
        with open(CONFIG_PATH, "w") as f:
            config[hunt_name] = data
            json.dump(config, f, indent=2)
        f.close()
        configHelper.print_linebreak()

    print(f"Config for {hunt_name} is ready!")
    configHelper.print_linebreak()

    return data