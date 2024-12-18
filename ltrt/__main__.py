from multiprocessing import Event
import time
from pathlib import Path

from ltrt.backend.run_realtime import run_realtime, shutdown_realtime

if __name__ == "__main__":
    stop_event = Event()
    calibration_toml_path = Path().home() /"freemocap_data/recording_sessions/freemocap_sample_data/freemocap_sample_data_camera_calibration.toml"
    processes = run_realtime(calibration_toml_path, stop_event)
    while not stop_event.is_set():
        time.sleep(0.1)
    shutdown_realtime(processes=processes)