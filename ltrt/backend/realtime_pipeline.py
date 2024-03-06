from multiprocessing.synchronize import Event as MultiprocessingEvent
import numpy as np
from skellytracker.trackers.base_tracker.base_tracker import BaseTracker
from queue import Empty

from web_of_cams.camera_frame_buffer import CameraFrameBuffer


def realtime_pipeline(camera_buffers: list[CameraFrameBuffer], trackers: dict[str, BaseTracker], stop_event: MultiprocessingEvent):
    frame_buffers = {buffer.cam_id: None for buffer in camera_buffers}
    cutoff = int((1 / camera_buffers[0].fps) * 1e9)

    for buffer in camera_buffers:
        if not buffer.outbound_queue:
            raise ValueError(
                f"Camera {buffer.cam_id} has no outbound queue!"
            )

    while not stop_event.is_set():
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
            tracker_data = []
            for buffer in camera_buffers:
                trackers[buffer.cam_id].process_image(frame_buffers[buffer.cam_id][0])
                output_array = trackers[buffer.cam_id].recorder.process_tracked_objects()
                tracker_data.append(output_array)

            combined_array = np.stack(tracker_data)
            print(combined_array.shape) # (1, 0, 17, 3) -> which seems a little weird

        # TODO: pass combined array into anipose and spit out 3D data!


