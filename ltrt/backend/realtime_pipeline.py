from multiprocessing import Queue
from typing import Optional
import numpy as np
from queue import Empty
from aniposelib.cameras import CameraGroup
from time import perf_counter_ns
import logging


from skellycam.core.frames.payloads.multi_frame_payload import MultiFramePayload

from skellytracker import YOLOPoseTracker

numba_logger = logging.getLogger('numba')
numba_logger.setLevel(logging.WARNING)
skellytracker_logger = logging.getLogger('skellytracker')
skellytracker_logger.setLevel(logging.WARNING)


def lightweight_realtime_pipeline(
    camera_group: CameraGroup,
    input_queue: Queue,
    output_queue: Queue,
    stop_event,
):
    # initialize tracker
    model_size = "nano"
    tracker = YOLOPoseTracker(model_size=model_size)
    start = perf_counter_ns()

    while not stop_event.is_set():
        # pull multiframe payload from queue
        start_queue = perf_counter_ns()
        try:
            multiframe_payload: Optional[MultiFramePayload] = input_queue.get(timeout=0.1)
        except Empty:
            continue
        end_queue = perf_counter_ns()
        print(f"queue pull took {(end_queue - start_queue) / 1e6} ms")

        if multiframe_payload is None:
            stop_event.set()
            break
        else:
            print(f"received multiframe payload number {multiframe_payload.multi_frame_number} with frame count {len(multiframe_payload.frames)}")

        # TODO: Frame payloads come in an arbitrary order - should we sort by Camera ID? 
        # or, just access by order of camID (are we guaranteed to have 0-N? or can there be missing values?)

        start_track = perf_counter_ns()
        tracker_data = []
        for frame_payload in multiframe_payload.frames.values():
            if frame_payload is None:
                print(f"multiframe payload frames: {multiframe_payload.frames}")
                raise ValueError("received None frame payload") # TODO: decide what to do for incomplete payloads
            tracker.process_image(frame_payload.image)
            tracker.recorder.record(tracked_objects=tracker.tracked_objects)
        combined_array = tracker.recorder.process_tracked_objects()[:, :, :2]
        tracker.recorder.clear_recorded_objects()

        print(f"combined array shape: {combined_array.shape}")

        end_track = perf_counter_ns()
        print(f"tracking took {(end_track - start_track) / 1e6} ms")

        # triangulate frame data with anipose
        start_triangulate = perf_counter_ns()
        triangulated_data = camera_group.triangulate(combined_array)
        print(f"triangulated data shape: {triangulated_data.shape}")
        end_triangulate = perf_counter_ns()
        print(f"triangulation took {(end_triangulate - start_triangulate) / 1e6} ms")
        # push 3d data to output queue
        # output_queue.put(triangulated_data)

        end = perf_counter_ns()
        print(f"processed frame {multiframe_payload.multi_frame_number} in {(end - start) / 1e6} ms")
        start = perf_counter_ns()

    # should we flush the queue here? 
    # i.e. if stop event is called but frames are still in the queue, should we cycle through until queue is empty?
    
    print("finished receiving multiframe payloads")


def heavyweight_realtime_pipeline(
    camera_group: CameraGroup,
    output_queue: Queue,
    stop_event,
):
    pass