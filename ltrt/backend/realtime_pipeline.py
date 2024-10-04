from multiprocessing import Queue
from typing import Optional
import numpy as np
from queue import Empty
from aniposelib.cameras import CameraGroup
from skellycam.core.frames.payloads.multi_frame_payload import MultiFramePayload


def lightweight_realtime_pipeline(
    camera_group: CameraGroup,
    input_queue: Queue,
    output_queue: Queue,
    stop_event,
):
    while not stop_event.is_set():
        # pull multiframe payload from queue
        try:
            multiframe_payload: Optional[MultiFramePayload] = input_queue.get(timeout=0.1)
        except Empty:
            continue

        if multiframe_payload is None:
            stop_event.set()
            break
        else:
            print(f"received multiframe payload number {multiframe_payload.multi_frame_number}")

        
        # process frames through skellytracker
        # we need to get a freemocap compatible output array out - for first attempt just make a tracker for each camera?
        # triangulate frame data with anipose
        # triangulated_data = camera_group.triangulate(combined_array)
        # push 3d data to output queue
        # output_queue.put(triangulated_data)

    # should we flush the queue here? 
    # i.e. if stop event is called but frames are still in the queue, should we cycle through until queue is empty?
    
    print("finished receiving multiframe payloads")


def heavyweight_realtime_pipeline(
    camera_group: CameraGroup,
    output_queue: Queue,
    stop_event,
):
    pass