import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

def create_new_recording_folder() -> str:
    new_recording_folder_path = Path.home() / "ltrt_recordings" / f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    new_recording_folder_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Creating new recording folder at: {new_recording_folder_path}")
    return str(new_recording_folder_path)

def create_new_recording_folder_path(recording_name: str):
    recording_folder_path = Path.home() / "ltrt_recordings" / recording_name
    recording_folder_path.mkdir(parents=True, exist_ok=True)

    return str(recording_folder_path)

def create_new_default_recording_name() -> str:
    full_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    recording_name = "recording_" + full_time
    return recording_name