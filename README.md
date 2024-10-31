# Let's Try Real Time

An isolated proof of concept for getting the FreeMoCap backend running in realtime. 

## Approach

Currently, it mocks realtime video capture by sending `MultiFramePayload` objects through a queue to the realtime process (happens in `mock_multiframe_payload.py`). The realtime pipeline pulls the payloads out of the queue, and sends each frame to a separate tracking process in separate `payload` queues, which then sends the resulting array back to the realtime pipeline in `output` queues. The arrays are then combined and triangulated, giving 3d data.

## Results

So far, this has been optimized from ~144 ms per frame for a naive version to ~70 ms per frame.

## Getting Started

Install with `pip install -e .` (or `uv pip install -e .`).

To run, run `__main__.py`.
