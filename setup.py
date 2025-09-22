from configuration import configureAudioDevice
from configuration import configureVideoDevice
from configuration import configureBoundingBox
from configuration import configureController
from configuration import configHelper

import json
import os

CONFIG_PATH = "config.json"
RESET_CONFIG_PATH = "game_reset_config.json"
HUNT_NAME_MANUAL = "mewtwo_bdsp"

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
        controller_ports = configureController.setup()
        data["controller_com_port"] = controller_ports["COM"]
        configHelper.print_linebreak()

    else:
        controller_ports = configureController.setup(uart_port=data["controller_com_port"])

    print("Controller Serial Ports Selected Sucessfully!")
    configHelper.print_linebreak()

    if "resets" not in keys:
        data["resets"] = 0
        needs_updating = True

    if "path" not in keys or os.path.isfile(data["path"]):
        os.makedirs(f"hunt/{hunt_name}", exist_ok=True)
        data["path"] = f"hunt/{hunt_name}"
        os.makedirs(f"hunt/{hunt_name}/screenshots", exist_ok=True)
        needs_updating = True

    if "roaming" not in keys:
        isRoaming = input("Roaming? (Y/N) ")
        while isRoaming.lower() not in ['y', 'n', 'yes', 'no']:
            isRoaming = input("Roaming? (Please use Y/N or Yes/No)")

        if isRoaming == 'y' or isRoaming == 'yes':
            data["roaming"] = True
        else:
            data["roaming"] = False
        needs_updating = True
    
    if "steps" not in keys:
        data["steps"] = 3
        print("Steps not found: setting to a placeholder (3)")


    # Rewrite config if needed
    if needs_updating or controller_ports["updated"]:
        print("Updating Config...")
        with open(CONFIG_PATH, "w") as f:
            config[hunt_name] = data
            json.dump(config, f, indent=2)
        f.close()
        configHelper.print_linebreak()
    else:
        print("No changes detected.")

    print(f"Config for {hunt_name} is ready!")
    configHelper.print_linebreak()

    return data

if __name__ == "__main__":
    testing = True
    if testing:
        # print(configureVideoDevice.list_video_devices())
        configureAudioDevice.testAudioDevice(2)
        # setup("cresselia_bdsp")
        # configureController.setup()
    else:
        print("hunt_name format -> pkmnName_gameName (i.e shaymin_bdsp, arceus_bdsp, registeel_swsh)")
        hunt = input("hunt_name (case sensitive): ")
        setup(hunt)
