# TODO:
Make a staged pipeline:
Try this again in a process that has an input queue.

Queue outputs packets that have a dict (~~MultiFrame.todict()), with multiframe, metadata...
key is cameraID, value is image. All images are synchronized coming in.

- spoof this by reading from videos

V1: At maximum quality, will it work and how long does it take?
    - max model quality, YOLO crop, postprocessing, etc.
V2: Sacrificing quality, can we beat 33ms?
    - can skip postprocessing

save data (just as basic numpy array), output some visualization