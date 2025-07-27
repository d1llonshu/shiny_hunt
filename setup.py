from configuration import configureAudioDevice
from configuration import configureVideoDevice
from configuration import configureBoundingBox
from configuration import configHelper

AUDIO_DEVICE = None #Should be set to None if you don't know the index or have restarted/unplugged
VIDEO_DEVICE = None #Should be set to None if you don't know the index or have restarted/unplugged
BOUNDING_BOX = () #Should be set to () if you don't know the bounding box region

def setup():
    print("Setting up Audio Device...")
    audio_device : configureAudioDevice.DeviceInfo = configureAudioDevice.setup(AUDIO_DEVICE)
    configHelper.print_linebreak()
    print("Setting up Video Device...")
    video_device : int = configureVideoDevice.setup(VIDEO_DEVICE)
    configHelper.print_linebreak()
    print("Setting up Bounding Box... ")
    bounding_box = configureBoundingBox.setup(video_device, BOUNDING_BOX)
    configHelper.print_linebreak()

setup()