from multiprocessing import Event, Queue, Process
from multiprocessing.synchronize import Event as MultiprocessingEvent
from pathlib import Path
import time
from skellytracker import YOLOPoseTracker

from aniposelib.cameras import CameraGroup

from web_of_cams.__main__ import setup_cameras
from web_of_cams.camera_frame_buffer import CameraFrameBuffer
from web_of_cams.process_handler import camera_process_handler_sm, shutdown_processes

from ltrt.backend.realtime_pipeline import realtime_pipeline

def run_realtime(calibration_toml_path: str | Path, stop_event: MultiprocessingEvent) -> tuple[list[CameraFrameBuffer], list[Process]]:
    camera_group = CameraGroup.load(str(calibration_toml_path))
    
    cam_buffers = setup_cameras(fps=30)
    for buffer in cam_buffers:
        buffer.outbound_queue = Queue(maxsize=3)

    trackers = {buffer.cam_id: YOLOPoseTracker() for buffer in cam_buffers}

    processes = camera_process_handler_sm(
        camera_buffers=cam_buffers,
        stop_event=stop_event)
    
    realtime_pipeline_process = Process(
        target=realtime_pipeline,
        args=(cam_buffers, trackers, camera_group, stop_event)
    )
    realtime_pipeline_process.start()
    processes.append(realtime_pipeline_process)

    time.sleep(5)

    return cam_buffers, processes

def shutdown_realtime(processes: list[Process], cam_buffers: list[CameraFrameBuffer], stop_event: MultiprocessingEvent) -> None:
    shutdown_processes(processes=processes, camera_buffers=cam_buffers, stop_event=stop_event)

if __name__ == "__main__":
    import cProfile
    import pstats
    stop_event = Event()
    calibration_toml_path = "/Users/philipqueen/freemocap_data/logs_info_and_settings/last_successful_calibration.toml"
    with cProfile.Profile() as profile:
        cam_buffers, processes = run_realtime(calibration_toml_path, stop_event)
        shutdown_realtime(processes=processes, cam_buffers=cam_buffers, stop_event=stop_event)

    # results = pstats.Stats(profile)
    # results.sort_stats(pstats.SortKey.TIME)
    # results.print_stats()