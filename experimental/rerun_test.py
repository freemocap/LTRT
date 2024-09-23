import time
import numpy as np
import rerun as rr

rr.init("rerun_viz")

rr.spawn()

data = np.load("/Users/philipqueen/freemocap_data/recording_sessions/freemocap_sample_data/freemocap_sample_data_frame_name_xyz.npy")

for i in range(data.shape[0]):
    rr.log("skeleton", rr.Points3D(data[i, :, :]))