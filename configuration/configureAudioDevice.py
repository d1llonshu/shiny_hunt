import sounddevice as sd
import soundfile as sf
import numpy as np
import os

from typing import TypedDict, List

from configuration.configHelper import print_linebreak, clear_folder, AUDIO_SAMPLES_PATH
from configuration.configHelper import AudioDeviceInfo as DeviceInfo

def getAudioDevices(target) -> List[DeviceInfo]:
    devices: List[DeviceInfo] = sd.query_devices() # type: ignore

    contains_target : List[DeviceInfo] = []

    for device in devices:
        if target.lower() in device["name"].lower():
            print_linebreak()
            volume = testAudioDevice(device_index=device["index"], samplerate=int(device["default_samplerate"]), channels=device["max_input_channels"])

            if volume > 0.0:
                contains_target.append(device)
            # contains_target[device["index"]] = device

    return contains_target


def testAudioDevice(device_index: int, samplerate: int = 44100, channels: int = 1) -> float:
    duration = 2.0
    try:
        recording = sd.rec(
            int(duration * samplerate),
            samplerate=samplerate,
            channels=channels,
            dtype='float32',
            device=device_index,
        )
        sd.wait()
        volume = float(np.abs(recording).mean())
        print(f"[Device {device_index}] Volume = {volume:.6f}")
    except Exception as e:
        print(f"[Device {device_index}] {e}")
        print(f"Write Succeeded: False")
        return -1.0
    
    out_path = os.path.join(AUDIO_SAMPLES_PATH, f"{device_index}.wav")

    try:
        sf.write(out_path, recording, samplerate, subtype='PCM_16')
        print("Write succeeded:", os.path.exists(out_path))
    except Exception as e:
        print("Write failed with:", repr(e))
    
    return volume

def setup(index=None) -> DeviceInfo:
    if index:
        print("Manually Provided Device: ")
        print(sd.query_devices(index))
        return sd.query_devices(index) # type: ignore
    # 1) Clear out old samples
    clear_folder(AUDIO_SAMPLES_PATH)

    # 2) Find at least one matching device
    while True:
        term = input("Enter device name search term: ")
        devices = getAudioDevices(term)
        if devices:
            break
        print(f"No valid devices found containing '{term}'. Please try again.")

    # 3) If there's exactly one, just return it
    if len(devices) == 1:
        print_linebreak()
        print("There was only 1 available device. It will be automatically selected.")
        print(f"Device {devices[0]['index']} (‘{devices[0]['name']}’).")
        return devices[0]

    # 4) Otherwise let the user pick from the remaining indices
    indices = [d["index"] for d in devices]
    print_linebreak()
    print("There is more than 1 available device.")
    print("You can look at samples/audio_setup_files/index.wav to listen to the recordings.") 
    print("Available device indices:", indices)
    while True:
        choice = input("Enter the device index you'd like to use: ")
        if choice.isdigit() and int(choice) in indices:
            sel = next(d for d in devices if d["index"] == int(choice))
            print(f"Selected device {sel['index']} (‘{sel['name']}’).")
            return sel
        print(f"Invalid choice '{choice}'. Please choose from {indices}.")


