from multiprocessing.synchronize import Event as MultiprocessingEvent
from multiprocessing import Queue
from typing import Optional
import numpy as np
from skellytracker.trackers.base_tracker.base_tracker import BaseTracker
from queue import Empty
from aniposelib.cameras import CameraGroup

from web_of_cams.camera_frame_buffer import CameraFrameBuffer


def realtime_pipeline(
    camera_buffers: list[CameraFrameBuffer],
    trackers: dict[str, BaseTracker],
    camera_group: CameraGroup,
    output_queue: Queue,
    stop_event: MultiprocessingEvent,
):
    frame_buffers: dict[str, Optional[tuple[np.ndarray, int]]] = {buffer.cam_id: None for buffer in camera_buffers}
    cutoff = int((1 / camera_buffers[0].fps) * 1e9)

    for buffer in camera_buffers:
        if not buffer.outbound_queue:
            raise ValueError(f"Camera {buffer.cam_id} has no outbound queue!")

    frame_count = 0
    while not stop_event.is_set():
        triangulate_bool = False
        for buffer in camera_buffers:
            if frame_buffers[buffer.cam_id] is None:
                try:
                    frame, timestamp = buffer.outbound_queue.get(timeout=0.5)
                    frame_buffers[buffer.cam_id] = (frame, timestamp)
                except Empty:
                    pass

        if (
            list(frame_buffers.values()).count(None) == 0
        ):  # only parse frame buffers if we have a candidate from each camera
            max_timestamp = max((timestamp for _, timestamp in frame_buffers.values()))
            for cam_id, (frame, timestamp) in frame_buffers.items():
                if max_timestamp - timestamp > cutoff:
                    frame_buffers[cam_id] = None  # throw out "early" frames
                    continue  # go look for next frame

        if (
            list(frame_buffers.values()).count(None) == 0
        ):  # buffer is synchronized at this point
            print(list(frame_buffers.values())[0][0][540, 860, :])
            tracker_data = []
            for buffer in camera_buffers:
                trackers[buffer.cam_id].process_image(frame_buffers[buffer.cam_id][0])
                output_array = trackers[
                    buffer.cam_id
                ].recorder.process_without_recording(
                    trackers[buffer.cam_id].tracked_objects
                )
                tracker_data.append(output_array)
                # print(output_array)

            combined_array = np.stack(tracker_data)
            combined_array = combined_array[:, :, :2]
            print(combined_array[0, 0, :])
            # print(combined_array.shape)
            triangulate_bool = True

        if triangulate_bool:
            triangulated_data = camera_group.triangulate(combined_array) # Turned off Numba JIT
            try:
                output_queue.put_nowait(triangulated_data)
            except Empty:
                pass
            frame_buffers = {buffer.cam_id: None for buffer in camera_buffers} 
            frame_count += 1


    print(f"frame count: {frame_count}")
