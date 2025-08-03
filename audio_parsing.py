import sounddevice as sd
import soundfile as sf
import librosa
import numpy as np
from scipy.signal import correlate
import json
import os
from setup import CONFIG_PATH

# === Configuration ===
REF_PATH = 'samples/reference_material/sparkle.mp3'  # Path to your 2-second sparkle sound
SAMPLE_RATE = 44100       # 44.1 kHz is standard
CHANNELS = 1              # Mono for simplicity
ROLLING_SECONDS = 2       # Length of rolling buffer (match reference duration)
BLOCK_DURATION = 0.25      # How often to check, in seconds (0.5s = 2Hz)
BLOCK_SIZE = int(SAMPLE_RATE * BLOCK_DURATION)

# Detection thresholds
# Cross-correlation threshold (lowest in testing seems to be 40+) 
# shaymin's call has peaked at 40.58 so we may want to raise
# strong matches are 400+
THRESHOLD_CORR = 200

save_path = ""

# # === Load and process reference sparkle sound ===
# === Normalize helper ===
def normalize_audio(y):
    return y / (np.max(np.abs(y)) + 1e-6)

# === Load and normalize reference sparkle audio ===
ref_audio, _ = librosa.load(REF_PATH, sr=SAMPLE_RATE, mono=True)
ref_audio = normalize_audio(ref_audio)

# === Initialize rolling buffer ===
rolling_buffer = np.zeros(SAMPLE_RATE * ROLLING_SECONDS)

# === Audio callback ===
def callback(indata, frames, time, status):
    global rolling_buffer

    if status:
        print(f"[!] Stream status: {status}")
        return

    # Flatten to mono
    audio_chunk = indata[:, 0] if indata.shape[1] > 1 else indata[:, 0]

    # Update buffer
    rolling_buffer = np.roll(rolling_buffer, -len(audio_chunk))
    rolling_buffer[-len(audio_chunk):] = audio_chunk

    # === Normalize rolling buffer ===
    buffer_norm = normalize_audio(rolling_buffer)

    # --- Cross-correlation ---
    corr = correlate(buffer_norm, ref_audio, mode='valid')
    max_corr = np.max(np.abs(corr))
    if max_corr >= 40:
        print(f"[Waveform] Max Corr: {max_corr:.2f}")

    # === Detection ===
    if max_corr > THRESHOLD_CORR:
        print("SHINY DETECTED!")
        sf.write(f"{save_path}/shiny.wav", buffer_norm, 44100)

def listen(device_index):
    # === Start audio stream ===
    # TO DO - IMPLEMENT PER HUNT PATH FOR SHINY_DETECTED
    # config_path = "config.json"
    # try:
    #     with open(config_path, "r") as f:
    #         config = json.load(f)
    # except Exception as e:
    #     print("Error with config or config path")
    print(save_path)
    try:
        with sd.InputStream(device=device_index, callback=callback,
                            channels=CHANNELS, samplerate=SAMPLE_RATE,
                            blocksize=BLOCK_SIZE):
            print(f"Listening for shiny sparkle... on Index [{device_index}]")
            while True:
                sd.sleep(1000)
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    # hunt = input("hunt_name (case sensitive): ")
    hunt = "shaymin_bdsp"
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
            data = config[hunt]
            shiny_folder = data["path"] + "/shiny_detected/"
            os.makedirs(shiny_folder, exist_ok=True)
            save_path = shiny_folder
            f.close()
        listen(data["audio_device_index"])
    except Exception as e:
        print(f"Error with config or config path: {e}")

    