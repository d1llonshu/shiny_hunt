import os
import shutil
from typing import TypedDict, List

HERE = os.path.dirname(__file__)                    
ROOT = os.path.abspath(os.path.join(HERE, os.pardir))  # …/Root
AUDIO_SAMPLES_PATH = os.path.join(ROOT, 'samples', 'audio_setup_files')
VIDEO_SAMPLES_PATH = os.path.join(ROOT, 'samples', 'video_setup_files')

class AudioDeviceInfo(TypedDict):
    name: str
    index: int
    hostapi: int
    max_input_channels: int
    max_output_channels: int
    default_low_input_latency: float
    default_low_output_latency: float
    default_high_input_latency: float
    default_high_output_latency: float
    default_samplerate: float

def clear_folder(path: str) -> None:
    """
    Delete all files and subfolders in `path`, but keep `path` itself.
    """
    for name in os.listdir(path):
        full_path = os.path.join(path, name)
        try:
            if os.path.isfile(full_path) or os.path.islink(full_path):
                os.unlink(full_path)                # remove file or symlink
            elif os.path.isdir(full_path):
                shutil.rmtree(full_path)            # remove directory and its contents
        except Exception as e:
            print(f"Failed to delete {full_path}: {e}")


def print_linebreak():
    print("-------------------------------")
